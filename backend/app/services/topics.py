"""TF-IDF keyphrase extraction engine.

Implements Term Frequency–Inverse Document Frequency (TF-IDF) from scratch
using only the Python standard library.

Design:
  - Accepts a corpus of documents and returns per-document ranked keyphrases.
  - Supports unigrams and bigrams.
  - IDF is computed once from the full corpus; TF is per-document.
  - A caller may nominate a single focus document (by index) to surface terms
    that distinguish that document from the rest of the corpus.
  - No hidden model state: every call is self-contained. See the ``ponytail``
    comment below on the ceiling of this approach and when to reach for a
    pre-fitted vectorizer.

Limitations (documented, not hidden):
  - Stop-word list is English-only. Non-English documents are not filtered.
  - TF-IDF is purely statistical and does not understand meaning or topics.
  - A corpus of fewer than two documents makes IDF degenerate (all terms share
    the same IDF score); a warning is placed in ``limitations``.
  - Extremely short documents (<3 tokens after normalization) produce sparse
    results; a warning is included.

ponytail: IDF fitted per-request; acceptable for small corpora (<1 k docs,
  <10 k tokens each). For larger corpora or repeated identical corpora, cache
  the IDF table keyed on a corpus fingerprint (e.g. hash of sorted doc hashes).
  Upgrade path: replace this module with a scikit-learn TfidfVectorizer fitted
  once at startup and stored in app state.
"""

from __future__ import annotations

import math
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# Constants & configuration
# ---------------------------------------------------------------------------

# Minimum documents in corpus for IDF to be meaningful.
_MIN_CORPUS_DOCS = 2

# Maximum documents accepted per request.
MAX_CORPUS_DOCS = 500

# Maximum characters per document.
MAX_DOC_CHARS = 50_000

# Default and maximum number of keyphrases returned per document.
DEFAULT_TOP_N = 10
MAX_TOP_N = 50

# n-gram sizes to extract (unigrams + bigrams by default).
_NGRAM_RANGE = (1, 2)

# ---------------------------------------------------------------------------
# English stop words
# Source: a curated subset of the SMART stop-word list, widely used in IR.
# Callers relying on non-English text should be aware these are English-only.
# ---------------------------------------------------------------------------
_STOP_WORDS: frozenset[str] = frozenset(
    {
        "a",
        "about",
        "above",
        "after",
        "again",
        "all",
        "also",
        "am",
        "an",
        "and",
        "any",
        "are",
        "as",
        "at",
        "be",
        "been",
        "before",
        "being",
        "below",
        "between",
        "both",
        "but",
        "by",
        "can",
        "could",
        "did",
        "do",
        "does",
        "doing",
        "down",
        "during",
        "each",
        "few",
        "for",
        "from",
        "further",
        "get",
        "got",
        "had",
        "has",
        "have",
        "having",
        "he",
        "her",
        "here",
        "hers",
        "herself",
        "him",
        "himself",
        "his",
        "how",
        "i",
        "if",
        "in",
        "into",
        "is",
        "it",
        "its",
        "itself",
        "just",
        "me",
        "more",
        "most",
        "my",
        "myself",
        "no",
        "not",
        "now",
        "of",
        "off",
        "on",
        "once",
        "only",
        "or",
        "other",
        "our",
        "ours",
        "out",
        "own",
        "s",
        "same",
        "she",
        "should",
        "so",
        "some",
        "such",
        "t",
        "than",
        "that",
        "the",
        "their",
        "theirs",
        "them",
        "then",
        "there",
        "these",
        "they",
        "this",
        "those",
        "through",
        "to",
        "too",
        "under",
        "until",
        "up",
        "us",
        "very",
        "was",
        "we",
        "were",
        "what",
        "when",
        "where",
        "which",
        "while",
        "who",
        "whom",
        "why",
        "will",
        "with",
        "you",
        "your",
        "yours",
        "yourself",
        "yourselves",
        "would",
    }
)

_WORD_RE = re.compile(r"[a-z]+(?:['-][a-z]+)*")


# ---------------------------------------------------------------------------
# Public data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Keyphrase:
    """A single extracted keyphrase with its TF-IDF score."""

    term: str
    score: float  # TF-IDF score, higher means more distinctive
    term_frequency: float  # Normalized TF within this document
    document_frequency: int  # Number of corpus docs containing this term
    ngram_size: int  # 1 = unigram, 2 = bigram


@dataclass
class DocumentTopics:
    """Keyphrase extraction result for a single document."""

    document_index: int
    keyphrases: list[Keyphrase]
    token_count: int
    limitations: list[str]


@dataclass
class TopicsResult:
    """Full TF-IDF keyphrase extraction result for a corpus."""

    corpus_size: int  # Number of documents analyzed
    focus_index: int | None  # None = all docs analyzed; int = focus document
    documents: list[DocumentTopics]
    preprocessing: dict[str, object]  # Configuration used
    limitations: list[str]  # Corpus-level warnings


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _normalize(text: str) -> str:
    """Unicode NFKC normalization, lowercase, URL/HTML stripping."""
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"https?://\S+|www\.\S+|\S+@\S+\.\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text.lower()


def _tokenize(text: str) -> list[str]:
    """Extract lowercase alpha tokens, filtering stop words and singles."""
    return [
        tok
        for tok in _WORD_RE.findall(_normalize(text))
        if tok not in _STOP_WORDS and len(tok) > 1
    ]


def _ngrams(tokens: list[str], n: int) -> list[str]:
    """Produce space-joined n-grams from a token list."""
    if n == 1:
        return list(tokens)
    return [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]


def _term_freq(tokens: list[str], n_min: int, n_max: int) -> Counter[str]:
    """Raw term counts for all n-gram sizes in [n_min, n_max]."""
    counts: Counter[str] = Counter()
    for n in range(n_min, n_max + 1):
        counts.update(_ngrams(tokens, n))
    return counts


def _idf(
    doc_token_lists: list[list[str]], n_min: int, n_max: int, corpus_size: int
) -> dict[str, float]:
    """
    Compute smoothed IDF for every term seen in the corpus.

    IDF(t) = log((1 + N) / (1 + df(t))) + 1   [sklearn-style smoothing]

    where N = corpus size, df(t) = number of documents containing term t.
    """
    df: Counter[str] = Counter()
    for tokens in doc_token_lists:
        seen_in_doc: set[str] = set()
        for n in range(n_min, n_max + 1):
            seen_in_doc.update(_ngrams(tokens, n))
        df.update(seen_in_doc)

    return {
        term: math.log((1 + corpus_size) / (1 + count)) + 1.0
        for term, count in df.items()
    }


def _score_document(
    tokens: list[str],
    idf_table: dict[str, float],
    n_min: int,
    n_max: int,
    top_n: int,
) -> list[Keyphrase]:
    """Compute TF-IDF for one document and return top-N Keyphrase objects."""
    tf_raw = _term_freq(tokens, n_min, n_max)
    total_terms = max(sum(tf_raw.values()), 1)

    scored: list[tuple[float, str]] = []
    for term, raw_count in tf_raw.items():
        idf_val = idf_table.get(term, 1.0)
        tf_norm = raw_count / total_terms
        tfidf = tf_norm * idf_val
        scored.append((tfidf, term))

    scored.sort(reverse=True)
    top = scored[:top_n]

    return [
        Keyphrase(
            term=term,
            score=round(score, 6),
            term_frequency=round(tf_raw[term] / total_terms, 6),
            document_frequency=0,  # filled in by caller with corpus df
            ngram_size=len(term.split()),
        )
        for score, term in top
    ]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_topics(
    documents: list[str],
    *,
    top_n: int = DEFAULT_TOP_N,
    focus_index: int | None = None,
) -> TopicsResult:
    """Extract TF-IDF keyphrases from a corpus of documents.

    Args:
        documents: List of raw text documents (reviews, descriptions, etc.).
        top_n: Maximum keyphrases to return per document. Capped at MAX_TOP_N.
        focus_index: If given, return keyphrases only for that document index
            (0-based). All other documents still contribute to IDF.

    Returns:
        TopicsResult with per-document keyphrases, preprocessing metadata,
        and corpus-level limitations.
    """
    top_n = min(max(1, top_n), MAX_TOP_N)
    n_min, n_max = _NGRAM_RANGE
    corpus_size = len(documents)

    corpus_limitations: list[str] = [
        "TF-IDF is a statistical ranking method. Scores reflect term "
        "distinctiveness within this corpus, not semantic meaning or topics.",
        "Stop-word filtering is English-only. Documents in other languages "
        "will include function words in their keyphrase lists.",
    ]

    if corpus_size < _MIN_CORPUS_DOCS:
        corpus_limitations.append(
            f"Corpus contains only {corpus_size} document(s). IDF is "
            "degenerate with fewer than 2 documents: all terms receive the "
            "same IDF weight, so scores reflect TF only."
        )

    # Tokenize corpus
    token_lists = [_tokenize(doc) for doc in documents]

    # Build IDF table from full corpus (always, regardless of focus_index)
    idf_table = _idf(token_lists, n_min, n_max, corpus_size)

    # Build document-frequency lookup for display
    df_lookup: Counter[str] = Counter()
    for tokens in token_lists:
        seen: set[str] = set()
        for n in range(n_min, n_max + 1):
            seen.update(_ngrams(tokens, n))
        df_lookup.update(seen)

    # Determine which documents to score
    indices_to_score = (
        [focus_index] if focus_index is not None else list(range(corpus_size))
    )

    doc_results: list[DocumentTopics] = []
    for idx in indices_to_score:
        tokens = token_lists[idx]
        doc_lims: list[str] = []
        if len(tokens) < 3:
            doc_lims.append(
                f"Document {idx} has only {len(tokens)} token(s) after "
                "preprocessing. Keyphrase results may be sparse or empty."
            )

        keyphrases = _score_document(tokens, idf_table, n_min, n_max, top_n)

        # Fill in document_frequency from df_lookup
        filled = [
            Keyphrase(
                term=kp.term,
                score=kp.score,
                term_frequency=kp.term_frequency,
                document_frequency=df_lookup[kp.term],
                ngram_size=kp.ngram_size,
            )
            for kp in keyphrases
        ]

        doc_results.append(
            DocumentTopics(
                document_index=idx,
                keyphrases=filled,
                token_count=len(tokens),
                limitations=doc_lims,
            )
        )

    return TopicsResult(
        corpus_size=corpus_size,
        focus_index=focus_index,
        documents=doc_results,
        preprocessing={
            "ngram_range": list(_NGRAM_RANGE),
            "stop_words": "english-smart-subset",
            "normalization": "NFKC-lowercase-url-html-strip",
            "min_token_length": 2,
            "top_n": top_n,
        },
        limitations=corpus_limitations,
    )
