"""Sentiment analysis & review polarity engine for ReviewPulse.

Zero-dependency rule- and lexicon-based sentiment analysis designed
specifically for consumer product reviews.

Features:
  - Calibrated valence dictionary for product review vocabulary
    (durability, performance, quality, customer support, defects, pricing).
  - Negation tracking ("not good", "never worked", "hardly usable").
  - Booster words / intensifiers ("very", "extremely", "barely", "slightly").
  - ALL-CAPS emphasis detection ("BROKEN", "FANTASTIC").
  - Exclamation mark amplification ("Great!").
  - Contrastive conjunction re-weighting ("Good design, but terrible battery").
  - Optional Aspect-Based Sentiment Analysis (ABSA) for target attributes
    (e.g., "battery", "screen", "shipping", "price").
  - Skew-resistant compound normalization in range [-1.0, +1.0].

ponytail: Rule/lexicon-based approach requires zero dependencies (stdlib only)
  and runs in <1 ms per review with deterministic output.
  Ceiling: Cannot detect complex sarcasm, nuanced figurative language, or
  multi-clause cross-sentence dependencies.
  Upgrade path: Fine-tuned RoBERTa / DeBERTa sentiment classifier or LLM prompt
  when GPU acceleration and heavy dependency footprints are acceptable.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Final

# ---------------------------------------------------------------------------
# Limits & Constants
# ---------------------------------------------------------------------------

MAX_TEXT_CHARS: Final[int] = 50_000
MAX_ASPECTS: Final[int] = 20
MAX_ASPECT_CHARS: Final[int] = 50

# Normalization parameter alpha (standard squashing parameter for compound score)
_NORMALIZATION_ALPHA: Final[float] = 15.0

# Boost factor for ALL-CAPS tokens
_ALL_CAPS_BOOSTER: Final[float] = 0.733

# Punctuation amplifications
_EXCLAMATION_BOOST: Final[float] = 0.292
_MAX_EXCLAMATION_BOOST: Final[float] = 0.876  # Cap at 3 exclamation marks

# Contrastive conjunction weights (dampen preceding clause, amplify succeeding clause)
_CONTRAST_BEFORE_FACTOR: Final[float] = 0.5
_CONTRAST_AFTER_FACTOR: Final[float] = 1.5

# Negation window and coefficient
_NEGATION_WINDOW: Final[int] = 3
_NEGATION_COEFFICIENT: Final[float] = -0.74

# ---------------------------------------------------------------------------
# Lexicon: Polar terms, Negators, Boosters, Contrastive Conjunctions
# ---------------------------------------------------------------------------

# Common negation terms in review texts
_NEGATIONS: Final[frozenset[str]] = frozenset(
    {
        "not",
        "no",
        "never",
        "neither",
        "nor",
        "hardly",
        "barely",
        "scarcely",
        "rarely",
        "cannot",
        "cant",
        "can't",
        "dont",
        "don't",
        "doesnt",
        "doesn't",
        "didnt",
        "didn't",
        "isnt",
        "isn't",
        "arent",
        "aren't",
        "wasnt",
        "wasn't",
        "werent",
        "weren't",
        "hasnt",
        "hasn't",
        "havent",
        "haven't",
        "hadnt",
        "hadn't",
        "wont",
        "won't",
        "wouldnt",
        "wouldn't",
        "shouldnt",
        "shouldn't",
        "couldnt",
        "couldn't",
        "without",
        "nothing",
        "nowhere",
        "none",
    }
)

# Booster words and their scalar modifiers
# (positive increases intensity, negative decreases)
_BOOSTERS: Final[dict[str, float]] = {
    # Strong amplifiers (+0.293)
    "absolutely": 0.293,
    "completely": 0.293,
    "extremely": 0.293,
    "really": 0.293,
    "very": 0.293,
    "super": 0.293,
    "highly": 0.293,
    "incredibly": 0.293,
    "totally": 0.293,
    "unbelievably": 0.293,
    "exceptionally": 0.293,
    "insanely": 0.293,
    "tremendously": 0.293,
    "decidedly": 0.25,
    "definitely": 0.25,
    "deeply": 0.25,
    "remarkably": 0.25,
    "thoroughly": 0.25,
    "vastly": 0.25,
    "quite": 0.20,
    "so": 0.20,
    "pretty": 0.15,
    "fairly": 0.15,
    # Dampeners / Downtoners (-0.293)
    "barely": -0.293,
    "hardly": -0.293,
    "scarcely": -0.293,
    "somewhat": -0.20,
    "mildly": -0.20,
    "slightly": -0.20,
    "marginally": -0.20,
    "partially": -0.15,
    "a bit": -0.15,
    "a little": -0.15,
    "kinda": -0.15,
    "kind of": -0.15,
    "sort of": -0.15,
}

# Contrastive conjunctions that pivot tone
_CONTRASTIVE_CONJUNCTIONS: Final[frozenset[str]] = frozenset(
    {
        "but",
        "however",
        "although",
        "though",
        "yet",
        "nevertheless",
        "nonetheless",
        "whereas",
        "except",
    }
)

# Curated polar review lexicon with baseline valence [-4.0 to +4.0]
_LEXICON: Final[dict[str, float]] = {
    # Strong positive (+3.0 to +4.0)
    "excellent": 3.2,
    "outstanding": 3.4,
    "superb": 3.3,
    "exceptional": 3.4,
    "fantastic": 3.3,
    "awesome": 3.2,
    "amazing": 3.4,
    "flawless": 3.3,
    "perfect": 3.4,
    "perfection": 3.3,
    "masterpiece": 3.5,
    "love": 3.1,
    "loved": 3.1,
    "loves": 3.1,
    "loving": 3.0,
    "delighted": 3.0,
    "delightful": 3.0,
    "wonderful": 3.1,
    "phenomenal": 3.4,
    "stellar": 3.2,
    "invaluable": 3.1,
    "breathtaking": 3.2,
    "stunning": 3.2,
    "beautiful": 3.0,
    "gorgeous": 3.1,
    "brilliant": 3.0,
    # Moderate positive (+1.5 to +2.9)
    "good": 1.9,
    "great": 2.5,
    "nice": 1.7,
    "well": 1.5,
    "fine": 1.3,
    "solid": 1.8,
    "reliable": 2.2,
    "durable": 2.3,
    "sturdy": 2.1,
    "efficient": 2.1,
    "fast": 1.8,
    "smooth": 1.9,
    "clean": 1.7,
    "crisp": 1.8,
    "bright": 1.6,
    "clear": 1.7,
    "sharp": 2.1,
    "comfortable": 2.2,
    "convenient": 2.0,
    "easy": 1.8,
    "intuitive": 2.1,
    "useful": 2.0,
    "helpful": 2.0,
    "recommend": 2.4,
    "recommended": 2.4,
    "recommending": 2.3,
    "pleased": 2.2,
    "satisfied": 2.1,
    "satisfying": 2.1,
    "impressive": 2.5,
    "impressed": 2.4,
    "valuable": 2.2,
    "worth": 1.9,
    "worthwhile": 2.1,
    "affordable": 1.8,
    "bonus": 1.7,
    "bargain": 2.0,
    "happy": 2.3,
    "glad": 2.0,
    "enjoy": 2.2,
    "enjoyed": 2.2,
    "enjoyable": 2.2,
    "best": 2.8,
    "better": 1.8,
    "upgrade": 1.9,
    "upgraded": 1.9,
    "favorite": 2.4,
    "favourite": 2.4,
    "prompt": 1.8,
    "polite": 1.8,
    "courteous": 2.0,
    "responsive": 2.0,
    "premium": 2.3,
    "sleek": 1.9,
    "elegant": 2.1,
    "quiet": 1.6,
    "safe": 1.9,
    "secure": 1.9,
    "flawlessly": 3.1,
    "smoothly": 2.0,
    # Mild positive (+0.5 to +1.4)
    "decent": 1.2,
    "adequate": 1.0,
    "acceptable": 1.0,
    "fair": 0.9,
    "passable": 0.8,
    "okay": 0.7,
    "ok": 0.7,
    "works": 1.1,
    "worked": 1.0,
    "fit": 1.1,
    "fits": 1.1,
    "handy": 1.4,
    "neat": 1.4,
    "proper": 1.2,
    "sufficient": 1.1,
    # Mild negative (-0.5 to -1.4)
    "mediocre": -1.2,
    "subpar": -1.3,
    "minor": -0.6,
    "slight": -0.5,
    "average": -0.3,
    "ordinary": -0.4,
    "plain": -0.4,
    "slow": -1.3,
    "clunky": -1.4,
    "bulky": -1.1,
    "heavy": -0.8,
    "warm": -0.5,
    "lukewarm": -1.0,
    "pricey": -1.2,
    "costly": -1.1,
    "expensive": -1.2,
    "overpriced": -1.8,
    "tricky": -1.0,
    "confusing": -1.4,
    "awkward": -1.3,
    "loud": -1.2,
    "noisy": -1.3,
    # Moderate negative (-1.5 to -2.9)
    "bad": -2.3,
    "poor": -2.2,
    "poorly": -2.2,
    "disappointed": -2.4,
    "disappointing": -2.5,
    "disappointment": -2.5,
    "unhappy": -2.2,
    "dissatisfied": -2.3,
    "flaw": -1.7,
    "flawed": -1.9,
    "defect": -2.1,
    "defective": -2.5,
    "fault": -1.8,
    "faulty": -2.3,
    "broken": -2.7,
    "broke": -2.6,
    "fail": -2.2,
    "failed": -2.4,
    "failure": -2.5,
    "failing": -2.3,
    "damage": -2.0,
    "damaged": -2.3,
    "damaging": -2.1,
    "cheap": -1.8,
    "flimsy": -2.2,
    "fragile": -1.9,
    "ugly": -2.0,
    "dirty": -1.8,
    "messy": -1.6,
    "annoying": -2.0,
    "annoyed": -2.0,
    "frustrating": -2.4,
    "frustrated": -2.3,
    "frustration": -2.3,
    "irritating": -2.0,
    "useless": -2.8,
    "worthless": -2.9,
    "junk": -2.8,
    "trash": -2.8,
    "garbage": -2.8,
    "waste": -2.5,
    "scam": -3.2,
    "misleading": -2.4,
    "return": -1.5,
    "returned": -1.8,
    "returning": -1.7,
    "refund": -1.8,
    "complaint": -1.9,
    "uncomfortable": -2.1,
    "inconvenient": -1.9,
    "difficult": -1.6,
    "unreliable": -2.6,
    "dull": -1.5,
    "blurry": -1.6,
    "glitch": -1.8,
    "glitchy": -2.0,
    "buggy": -2.1,
    "stuck": -1.8,
    "freeze": -1.8,
    "freezes": -1.9,
    "froze": -1.9,
    "crash": -2.4,
    "crashed": -2.5,
    "crashes": -2.4,
    "dead": -2.4,
    "died": -2.4,
    "dies": -2.3,
    "unacceptable": -2.7,
    # Strong negative (-3.0 to -4.0)
    "terrible": -3.4,
    "horrible": -3.4,
    "awful": -3.3,
    "atrocious": -3.5,
    "dreadful": -3.4,
    "appalling": -3.5,
    "disastrous": -3.6,
    "abysmal": -3.5,
    "unusable": -3.3,
    "worst": -3.5,
    "hate": -3.2,
    "hated": -3.2,
    "hates": -3.1,
    "hating": -3.0,
    "nightmare": -3.4,
    "pathetic": -3.2,
    "repulsive": -3.3,
    "ruined": -3.1,
    "lemon": -2.6,
    "rip-off": -3.3,
    "ripoff": -3.3,
    "counterfeit": -3.5,
    "fake": -3.2,
}

# ---------------------------------------------------------------------------
# Data Classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PolarHighlight:
    """A polar token in the text that influenced the sentiment score."""

    token: str
    raw_valence: float
    adjusted_valence: float
    modifiers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class AspectSentimentResult:
    """Sentiment result for a specific product aspect."""

    aspect: str
    compound: float
    label: str
    mentions_count: int
    snippets: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SentimentScores:
    """Breakdown of sentiment scores."""

    compound: float
    positive: float
    negative: float
    neutral: float


@dataclass(frozen=True)
class SentimentResult:
    """Full result of the sentiment analysis."""

    text_length: int
    word_count: int
    scores: SentimentScores
    label: str
    confidence: float
    highlights: list[PolarHighlight]
    aspects: dict[str, AspectSentimentResult]
    limitations: list[str]


# ---------------------------------------------------------------------------
# Tokenization & Normalization
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[A-Za-z0-9'\-]+|[!?,;.]")
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def _is_all_caps(token: str) -> bool:
    """Check if token is at least 2 chars and all uppercase."""
    return len(token) > 1 and token.isupper() and token.isalpha()


def _normalize_token(raw_token: str) -> str:
    """Normalize unicode and strip trailing apostrophes/hyphens."""
    token = unicodedata.normalize("NFKD", raw_token).strip("'-")
    return token.lower()


# ---------------------------------------------------------------------------
# Sentiment Evaluation Engine
# ---------------------------------------------------------------------------


def _normalize_compound(score: float, alpha: float = _NORMALIZATION_ALPHA) -> float:
    """Squash raw score sum to [-1.0, 1.0] using hyperbolic-style curve."""
    return round(score / math.sqrt((score * score) + alpha), 4)


def _determine_label(compound: float) -> str:
    """Assign categorical label based on compound score."""
    if compound >= 0.05:
        return "positive"
    if compound <= -0.05:
        return "negative"
    return "neutral"


def _calculate_component_scores(
    valences: list[float], total_words: int
) -> tuple[float, float, float]:
    """Calculate pos, neg, neu proportion scores summing to 1.0."""
    if not valences or total_words == 0:
        return 0.0, 0.0, 1.0

    pos_sum = sum(v for v in valences if v > 0)
    neg_sum = abs(sum(v for v in valences if v < 0))

    # Base total includes neutral words
    raw_total = pos_sum + neg_sum + max(0, total_words - len(valences))
    if raw_total <= 0:
        return 0.0, 0.0, 1.0

    pos_score = round(pos_sum / raw_total, 3)
    neg_score = round(neg_sum / raw_total, 3)
    neu_score = round(max(0.0, 1.0 - (pos_score + neg_score)), 3)

    return pos_score, neg_score, neu_score


def _score_sentence_tokens(tokens: list[str]) -> list[PolarHighlight]:
    """Score a sequence of tokens from a single sentence or clause."""
    highlights: list[PolarHighlight] = []

    # Check exclamation marks count in this clause
    exclamation_count = sum(1 for t in tokens if t == "!")
    punct_multiplier = 1.0 + min(
        _MAX_EXCLAMATION_BOOST, exclamation_count * _EXCLAMATION_BOOST
    )

    # Check if this clause contains contrastive pivot
    contrast_pivot = False
    clause_factor = 1.0

    for i, tok in enumerate(tokens):
        if tok in _CONTRASTIVE_CONJUNCTIONS:
            contrast_pivot = True
            continue

        lower_tok = _normalize_token(tok)
        if lower_tok not in _LEXICON:
            continue

        raw_valence = _LEXICON[lower_tok]
        adjusted = raw_valence
        modifiers: list[str] = []

        # 1. Check ALL CAPS
        if _is_all_caps(tok):
            caps_bump = _ALL_CAPS_BOOSTER if raw_valence > 0 else -_ALL_CAPS_BOOSTER
            adjusted += caps_bump
            modifiers.append("ALL_CAPS")

        # 2. Check preceding tokens in negation / booster window
        start_idx = max(0, i - _NEGATION_WINDOW)
        window = tokens[start_idx:i]

        is_negated = False
        booster_sum = 0.0

        for dist, prev_tok in enumerate(reversed(window), start=1):
            prev_lower = _normalize_token(prev_tok)
            # Check negation
            if prev_lower in _NEGATIONS:
                is_negated = True
                modifiers.append(f"negated_by('{prev_lower}')")
                break
            # Check booster
            if prev_lower in _BOOSTERS:
                b_val = _BOOSTERS[prev_lower]
                # Modulate booster if capitalized
                if _is_all_caps(prev_tok):
                    b_val = b_val * 1.5
                # Distance dampener (further tokens have less boost)
                dist_factor = 1.0 if dist == 1 else (0.8 if dist == 2 else 0.6)
                booster_sum += b_val * dist_factor
                modifiers.append(f"boosted_by('{prev_lower}')")

        if booster_sum != 0.0:
            if adjusted > 0:
                adjusted += booster_sum
            else:
                adjusted -= booster_sum

        if is_negated:
            adjusted = adjusted * _NEGATION_COEFFICIENT

        # 3. Apply punctuation multiplier
        if exclamation_count > 0:
            adjusted *= punct_multiplier
            modifiers.append(f"exclamations({exclamation_count})")

        # 4. Apply contrastive factor if clause is before/after "but"
        clause_factor = (
            _CONTRAST_AFTER_FACTOR if contrast_pivot else _CONTRAST_BEFORE_FACTOR
        )
        if contrast_pivot:
            modifiers.append("after_contrast_conjunction")
            adjusted *= clause_factor
        elif any(t in _CONTRASTIVE_CONJUNCTIONS for t in tokens):
            modifiers.append("before_contrast_conjunction")
            adjusted *= clause_factor

        highlights.append(
            PolarHighlight(
                token=tok,
                raw_valence=raw_valence,
                adjusted_valence=round(adjusted, 4),
                modifiers=modifiers,
            )
        )

    return highlights


def _extract_aspect_sentiments(
    text: str,
    aspects: list[str],
) -> dict[str, AspectSentimentResult]:
    """Evaluate aspect-targeted sentiments across sentence windows."""
    results: dict[str, AspectSentimentResult] = {}
    sentences = _SENTENCE_SPLIT_RE.split(text.strip())

    for raw_aspect in aspects:
        clean_aspect = raw_aspect.strip().lower()
        if not clean_aspect:
            continue

        aspect_pattern = re.compile(rf"\b{re.escape(clean_aspect)}\b", re.IGNORECASE)
        matching_sentences: list[str] = []
        clause_valences: list[float] = []

        for sent in sentences:
            if aspect_pattern.search(sent):
                clean_sent = sent.strip()
                if clean_sent:
                    matching_sentences.append(clean_sent)
                tokens = _TOKEN_RE.findall(clean_sent)
                clause_highlights = _score_sentence_tokens(tokens)
                for h in clause_highlights:
                    clause_valences.append(h.adjusted_valence)

        mentions_count = len(matching_sentences)
        if mentions_count == 0:
            results[raw_aspect] = AspectSentimentResult(
                aspect=raw_aspect,
                compound=0.0,
                label="neutral",
                mentions_count=0,
                snippets=[],
            )
            continue

        aspect_raw_score = sum(clause_valences)
        aspect_compound = _normalize_compound(aspect_raw_score)
        aspect_label = _determine_label(aspect_compound)

        results[raw_aspect] = AspectSentimentResult(
            aspect=raw_aspect,
            compound=aspect_compound,
            label=aspect_label,
            mentions_count=mentions_count,
            snippets=matching_sentences[:3],
        )

    return results


# ---------------------------------------------------------------------------
# Public Service API
# ---------------------------------------------------------------------------


def analyze_sentiment(
    text: str,
    aspects: list[str] | None = None,
) -> SentimentResult:
    """Analyze sentiment polarity and intensity of a review text.

    Args:
        text: The consumer review text.
        aspects: Optional list of specific product attributes to score
            (e.g., ["battery", "camera", "price"]).

    Returns:
        SentimentResult containing compound, pos/neg/neu breakdown,
        label, confidence, polar highlights, aspect sentiments, and limitations.
    """
    limitations: list[str] = []
    clean_text = text.strip()

    if not clean_text:
        return SentimentResult(
            text_length=0,
            word_count=0,
            scores=SentimentScores(
                compound=0.0, positive=0.0, negative=0.0, neutral=1.0
            ),
            label="neutral",
            confidence=0.0,
            highlights=[],
            aspects={},
            limitations=["Empty or whitespace-only review text received."],
        )

    # Split into sentences for clause-aware evaluation
    sentences = _SENTENCE_SPLIT_RE.split(clean_text)
    all_highlights: list[PolarHighlight] = []
    total_words = 0

    for sent in sentences:
        tokens = _TOKEN_RE.findall(sent)
        words_in_sent = [t for t in tokens if any(c.isalnum() for c in t)]
        total_words += len(words_in_sent)
        sent_highlights = _score_sentence_tokens(tokens)
        all_highlights.extend(sent_highlights)

    if total_words == 0:
        return SentimentResult(
            text_length=len(text),
            word_count=0,
            scores=SentimentScores(
                compound=0.0, positive=0.0, negative=0.0, neutral=1.0
            ),
            label="neutral",
            confidence=0.0,
            highlights=[],
            aspects={},
            limitations=["Text contains only punctuation or whitespace."],
        )

    valences = [h.adjusted_valence for h in all_highlights]
    raw_sum = sum(valences)
    compound = _normalize_compound(raw_sum)
    label = _determine_label(compound)

    pos_score, neg_score, neu_score = _calculate_component_scores(valences, total_words)

    # Confidence metric derived from absolute compound and margin over neutral
    confidence = round(min(1.0, abs(compound) + (0.2 if len(valences) > 0 else 0.0)), 3)
    if label == "neutral" and len(valences) == 0:
        confidence = 0.5

    # Process aspect-based sentiments if requested
    aspect_results: dict[str, AspectSentimentResult] = {}
    if aspects:
        aspect_results = _extract_aspect_sentiments(clean_text, aspects)

    if len(valences) == 0:
        limitations.append(
            "No polar vocabulary from the lexicon was detected in the review text."
        )

    if len(clean_text) < 15:
        limitations.append(
            "Very short text; sentiment estimation has lower confidence."
        )

    return SentimentResult(
        text_length=len(text),
        word_count=total_words,
        scores=SentimentScores(
            compound=compound,
            positive=pos_score,
            negative=neg_score,
            neutral=neu_score,
        ),
        label=label,
        confidence=confidence,
        highlights=all_highlights,
        aspects=aspect_results,
        limitations=limitations,
    )
