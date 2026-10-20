"""Product intelligence service.

Aggregates review sentiment, TF-IDF topics, ratings, and readability metrics
on-demand for a given product.
"""

from __future__ import annotations

import logging
from collections import Counter, defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.review import Review
from app.schemas.harvester import (
    AspectInsight,
    ProductInsightsResponse,
    RatingBreakdown,
    ReadabilitySummary,
    SentimentCounts,
    SentimentInsightSummary,
    TopicInsight,
)
from app.services.readability import calculate_readability, interpret_grade_level
from app.services.sentiment import analyze_sentiment
from app.services.topics import extract_topics

logger = logging.getLogger(__name__)


async def compute_product_insights(
    session: AsyncSession,
    product_id: str,
    limit: int = 100,
    aspects: list[str] | None = None,
) -> ProductInsightsResponse | None:
    """Compute aggregated review insights for a product on demand."""
    # 1. Verify product existence
    product_result = await session.execute(
        select(Product).where(Product.product_id == product_id)
    )
    product = product_result.scalar_one_or_none()
    if product is None:
        return None

    # 2. Total reviews count in DB
    count_stmt = select(func.count(Review.id)).where(Review.product_id == product_id)
    total_reviews_in_db = (await session.execute(count_stmt)).scalar() or 0

    # 3. Query reviews sample up to limit
    reviews_stmt = (
        select(Review)
        .where(Review.product_id == product_id)
        .order_by(Review.id)
        .limit(limit)
    )
    reviews = list((await session.execute(reviews_stmt)).scalars().all())

    # 4. Rating statistics breakdown
    star_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    valid_ratings: list[float] = []
    for r in reviews:
        if r.rating is not None:
            valid_ratings.append(r.rating)
            star = max(1, min(5, round(r.rating)))
            star_counts[star] += 1

    avg_rating = (
        round(sum(valid_ratings) / len(valid_ratings), 2)
        if valid_ratings
        else product.rating
    )
    ratings_breakdown = RatingBreakdown(
        average_rating=avg_rating,
        total_ratings_count=len(valid_ratings),
        stars_1=star_counts[1],
        stars_2=star_counts[2],
        stars_3=star_counts[3],
        stars_4=star_counts[4],
        stars_5=star_counts[5],
    )

    # 5. Extract analyzable review texts
    analyzable_texts: list[str] = []
    for r in reviews:
        content = (r.review_content or "").strip()
        title = (r.review_title or "").strip()
        if content and title:
            text = f"{title}. {content}"
        elif content:
            text = content
        elif title:
            text = title
        else:
            continue
        analyzable_texts.append(text)

    # 6. Analyze texts (or default empty response if no text available)
    if not analyzable_texts:
        return ProductInsightsResponse(
            product_id=product.product_id,
            product_name=product.product_name,
            total_reviews_in_db=total_reviews_in_db,
            total_reviews_analyzed=0,
            ratings=ratings_breakdown,
            sentiment=SentimentInsightSummary(),
            top_topics=[],
            readability=ReadabilitySummary(),
        )

    # Sentiment analysis
    sentiment_results = [
        analyze_sentiment(text, aspects=aspects) for text in analyzable_texts
    ]
    compounds = [sr.scores.compound for sr in sentiment_results]
    avg_compound = round(sum(compounds) / len(compounds), 3) if compounds else 0.0

    if avg_compound >= 0.05:
        overall_label = "positive"
    elif avg_compound <= -0.05:
        overall_label = "negative"
    else:
        overall_label = "neutral"

    pos_cnt = sum(1 for sr in sentiment_results if sr.label == "positive")
    neu_cnt = sum(1 for sr in sentiment_results if sr.label == "neutral")
    neg_cnt = sum(1 for sr in sentiment_results if sr.label == "negative")

    pos_tokens: Counter[str] = Counter()
    neg_tokens: Counter[str] = Counter()
    for sr in sentiment_results:
        for h in sr.highlights:
            token_clean = h.token.lower()
            if h.adjusted_valence > 0:
                pos_tokens[token_clean] += 1
            elif h.adjusted_valence < 0:
                neg_tokens[token_clean] += 1

    top_pos_highlights = [t for t, _ in pos_tokens.most_common(5)]
    top_neg_highlights = [t for t, _ in neg_tokens.most_common(5)]

    # Aggregated aspect insights
    aspect_insights: dict[str, AspectInsight] = {}
    if aspects:
        for aspect_name in aspects:
            asp_compounds: list[float] = []
            asp_snippets: list[str] = []
            total_mentions = 0
            for sr in sentiment_results:
                asp_data = sr.aspects.get(aspect_name)
                if asp_data and asp_data.mentions_count > 0:
                    asp_compounds.append(asp_data.compound)
                    total_mentions += asp_data.mentions_count
                    for snip in asp_data.snippets:
                        if len(asp_snippets) < 3 and snip not in asp_snippets:
                            asp_snippets.append(snip)

            if asp_compounds:
                avg_asp_comp = round(sum(asp_compounds) / len(asp_compounds), 3)
                if avg_asp_comp >= 0.05:
                    asp_label = "positive"
                elif avg_asp_comp <= -0.05:
                    asp_label = "negative"
                else:
                    asp_label = "neutral"
            else:
                avg_asp_comp = 0.0
                asp_label = "neutral"

            aspect_insights[aspect_name] = AspectInsight(
                aspect=aspect_name,
                average_polarity=avg_asp_comp,
                label=asp_label,
                mentions_count=total_mentions,
                snippets=asp_snippets,
            )

    sentiment_summary = SentimentInsightSummary(
        average_polarity=avg_compound,
        sentiment_label=overall_label,
        counts=SentimentCounts(positive=pos_cnt, neutral=neu_cnt, negative=neg_cnt),
        top_positive_highlights=top_pos_highlights,
        top_negative_highlights=top_neg_highlights,
        aspects=aspect_insights,
    )

    # Topics extraction
    top_topics: list[TopicInsight] = []
    try:
        topics_result = extract_topics(analyzable_texts, top_n=10)
        term_scores: dict[str, float] = defaultdict(float)
        term_freqs: dict[str, int] = defaultdict(int)
        term_ngrams: dict[str, int] = {}

        for doc in topics_result.documents:
            for kp in doc.keyphrases:
                term_scores[kp.term] = max(term_scores[kp.term], kp.score)
                term_freqs[kp.term] += 1
                term_ngrams[kp.term] = kp.ngram_size

        sorted_terms = sorted(
            term_scores.keys(),
            key=lambda t: (term_scores[t], term_freqs[t]),
            reverse=True,
        )[:10]

        top_topics = [
            TopicInsight(
                term=t,
                relevance_score=round(term_scores[t], 4),
                frequency=term_freqs[t],
                ngram_size=term_ngrams[t],
            )
            for t in sorted_terms
        ]
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Topic extraction failed for product %s: %s", product.product_id, exc
        )

    # Readability calculation
    reading_ease_scores: list[float] = []
    grade_levels: list[float] = []
    for text in analyzable_texts:
        rep = calculate_readability(text)
        if rep.is_analyzable and rep.flesch_reading_ease.score is not None:
            reading_ease_scores.append(rep.flesch_reading_ease.score)
        if rep.is_analyzable and rep.consensus_grade_level is not None:
            grade_levels.append(rep.consensus_grade_level)

    avg_ease = (
        round(sum(reading_ease_scores) / len(reading_ease_scores), 2)
        if reading_ease_scores
        else None
    )
    avg_grade = (
        round(sum(grade_levels) / len(grade_levels), 1) if grade_levels else None
    )
    grade_label = interpret_grade_level(avg_grade) if avg_grade is not None else None

    readability_summary = ReadabilitySummary(
        average_reading_ease=avg_ease,
        consensus_grade_level=avg_grade,
        reading_level_label=grade_label,
    )

    return ProductInsightsResponse(
        product_id=product.product_id,
        product_name=product.product_name,
        total_reviews_in_db=total_reviews_in_db,
        total_reviews_analyzed=len(analyzable_texts),
        ratings=ratings_breakdown,
        sentiment=sentiment_summary,
        top_topics=top_topics,
        readability=readability_summary,
    )
