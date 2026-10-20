"""Linguistic complexity and readability analysis engine.

Provides deterministic, zero-dependency text analysis implementing classic,
peer-reviewed readability formulas calibrated for English prose:
- Flesch Reading Ease (Flesch, 1948)
- Flesch-Kincaid Grade Level (Kincaid et al., 1975)
- Gunning Fog Index (Gunning, 1952)
- Coleman-Liau Index (Coleman & Liau, 1975)
- Automated Readability Index (Senter & Smith, 1967)

Independent from FastAPI routing for CLI, worker, or test reuse.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass
from typing import Literal

ReliabilityLevel = Literal["high", "medium", "low", "unreliable"]

# Common abbreviations to prevent premature sentence segmentation
_ABBREVIATIONS = frozenset(
    {
        "mr",
        "mrs",
        "ms",
        "dr",
        "prof",
        "sr",
        "jr",
        "vs",
        "etc",
        "inc",
        "ltd",
        "corp",
        "co",
        "st",
        "ave",
        "rd",
        "blvd",
        "dept",
        "est",
        "approx",
        "fig",
        "no",
        "vol",
        "i.e",
        "e.g",
        "u.s",
        "u.k",
        "a.m",
        "p.m",
        "jan",
        "feb",
        "mar",
        "apr",
        "jun",
        "jul",
        "aug",
        "sep",
        "sept",
        "oct",
        "nov",
        "dec",
    }
)

# Regex patterns for tokenization
_WORD_RE = re.compile(r"\b[a-zA-Z]+(?:['’-][a-zA-Z]+)*\b")
_HONORIFICS_RE = re.compile(
    r"\b(Mr|Mrs|Ms|Dr|Prof|Sr|Jr|vs|etc|i\.e|e\.g)\.",
    re.IGNORECASE,
)
_INITIALS_RE = re.compile(r"\b([A-Z])\.")
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


@dataclass(frozen=True)
class TextStatistics:
    """Core descriptive statistics for a analyzed text sample."""

    character_count: int
    letter_count: int
    word_count: int
    sentence_count: int
    syllable_count: int
    complex_word_count: int
    unique_word_count: int
    avg_words_per_sentence: float
    avg_syllables_per_word: float
    avg_letters_per_word: float
    complex_word_percentage: float
    type_token_ratio: float


@dataclass(frozen=True)
class ReadabilityScore:
    """Individual readability formula calculation result."""

    score: float | None
    grade_level: float | None
    interpretation: str | None
    description: str


@dataclass(frozen=True)
class ReadabilityReport:
    """Comprehensive linguistic complexity and readability audit result."""

    is_analyzable: bool
    reliability: ReliabilityLevel
    language: str
    statistics: TextStatistics
    flesch_reading_ease: ReadabilityScore
    flesch_kincaid_grade: ReadabilityScore
    gunning_fog: ReadabilityScore
    coleman_liau: ReadabilityScore
    automated_readability_index: ReadabilityScore
    consensus_grade_level: float | None
    reading_time_seconds: float
    limitations: list[str]

    def to_dict(self) -> dict:
        """Convert report to dictionary representation."""
        return asdict(self)


def normalize_text(text: str) -> str:
    """Safely normalize Unicode while preserving sentence and punctuation integrity."""
    normalized = unicodedata.normalize("NFKC", text)
    # Replace non-breaking spaces with standard space
    normalized = normalized.replace("\u00a0", " ").replace("\u200b", "")
    return normalized.strip()


def extract_sentences(text: str) -> list[str]:
    """Segment text into individual sentences, respecting abbreviations and numbers."""
    if not text:
        return []

    clean = re.sub(r"[ \t]+", " ", text).strip()
    if not clean:
        return []

    # Mask known abbreviations and single letter initials to avoid premature splitting
    masked = _HONORIFICS_RE.sub(r"\1<DOT>", clean)
    masked = _INITIALS_RE.sub(r"\1<DOT>", masked)
    masked = re.sub(r"(\d+)\.(\d+)", r"\1<DOT>\2", masked)

    # Split on sentence terminals (. ! ?) followed by whitespace
    raw_splits = re.split(r"(?<=[.!?])\s+", masked)

    sentences: list[str] = []
    for s in raw_splits:
        restored = s.replace("<DOT>", ".").strip()
        if any(c.isalnum() for c in restored):
            sentences.append(restored)

    return sentences


def extract_words(text: str) -> list[str]:
    """Extract individual linguistic words, ignoring standalone punctuation."""
    return _WORD_RE.findall(text)


def count_syllables_in_word(word: str) -> int:
    """Estimate English syllables using rule-based morphological heuristics.

    Rules applied:
    1. Lowercase and trim non-alphabetic boundaries.
    2. Words of 3 letters or fewer count as 1 syllable.
    3. Count consecutive vowel groups ([aeiouy]+).
    4. Handle silent trailing 'e' (except '-le' preceded by consonant).
    5. Handle silent '-ed' (except when preceded by 'd' or 't').
    6. Handle silent '-es' (except when preceded by s, z, x, ch, sh).
    7. Account for vowel splits (e.g. 'ia', 'io' in dial, lion).
    8. Enforce minimum of 1 syllable.
    """
    cleaned = word.lower().strip()
    cleaned = re.sub(r"^[^a-z]+|[^a-z]+$", "", cleaned)
    if not cleaned:
        return 0

    if len(cleaned) <= 3:
        return 1

    # Base count of vowel clusters
    vowel_matches = _VOWEL_GROUP_RE.findall(cleaned)
    count = len(vowel_matches)

    # Silent 'e' at the end: 'rate', 'make', 'game'
    if cleaned.endswith("e") and not cleaned.endswith(("ee", "oe")):
        # Check for '-le' preceded by consonant (e.g. 'apple', 'little')
        if len(cleaned) >= 3 and cleaned[-2] == "l" and cleaned[-3] not in "aeiouy":
            pass
        else:
            count -= 1

    # Silent '-ed': 'asked' (1), 'played' (1), but 'hated' (2), 'waited' (2)
    elif cleaned.endswith("ed") and len(cleaned) > 3:
        preceding = cleaned[-3]
        if preceding not in ("d", "t"):
            count -= 1

    # Silent '-es': 'rates' (1), 'games' (1), but 'classes' (2), 'boxes' (2)
    elif cleaned.endswith("es") and len(cleaned) > 3:
        preceding = cleaned[-3]
        if preceding not in ("s", "z", "x") and not cleaned.endswith(("ches", "shes")):
            count -= 1

    # Diphthong split expansions (e.g. 'dial', 'lion', 'science', 'triumph')
    if re.search(r"[a-z](?:ia|io|iu)[a-z]*$", cleaned):
        count += 1

    return max(1, count)


def is_complex_word(word: str, syllable_count: int | None = None) -> bool:
    """Identify if a word is complex (>= 3 syllables) by Gunning Fog standards."""
    syllables = (
        syllable_count if syllable_count is not None else count_syllables_in_word(word)
    )
    if syllables < 3:
        return False
    # Exclude common suffixes that artificially inflate syllable count
    cleaned = word.lower()
    if cleaned.endswith(("ing", "ed", "es")) and syllables == 3:
        # Check root word syllables
        root = re.sub(r"(ing|ed|es)$", "", cleaned)
        if count_syllables_in_word(root) < 3:
            return False
    return True


def interpret_flesch_reading_ease(score: float) -> str:
    """Map Flesch Reading Ease score to standard comprehension levels."""
    if score >= 90.0:
        return (
            "Very Easy (5th grade reading level; easily understood by "
            "an average 10-year-old)"
        )
    if score >= 80.0:
        return "Easy (6th grade reading level; conversational plain English)"
    if score >= 70.0:
        return "Fairly Easy (7th grade reading level)"
    if score >= 60.0:
        return "Standard (8th-9th grade reading level; standard consumer text)"
    if score >= 50.0:
        return "Fairly Difficult (10th-12th grade reading level; high school)"
    if score >= 30.0:
        return "Difficult (College academic level)"
    return "Very Confusing (Graduate level / technical professional prose)"


def interpret_grade_level(grade: float) -> str:
    """Translate numerical US school grade level to qualitative educational range."""
    if grade <= 5.0:
        return f"Elementary School (~Grade {max(1, round(grade))})"
    if grade <= 8.0:
        return f"Middle School (~Grade {round(grade)})"
    if grade <= 12.0:
        return f"High School (~Grade {round(grade)})"
    if grade <= 16.0:
        return f"College Undergraduate (~Year {round(grade) - 12})"
    return "Graduate / Professional Degree Level"


def calculate_readability(text: str) -> ReadabilityReport:
    """Perform readability and linguistic complexity analysis on input text.

    Args:
        text: Raw text string to analyze.

    Returns:
        ReadabilityReport with statistics, metrics, and reliability notes.
    """
    clean_text = normalize_text(text)
    limitations: list[str] = [
        "Calibrated exclusively for English prose (en). "
        "Non-English text metrics will not be accurate.",
    ]

    # Extract tokens
    words = extract_words(clean_text)
    sentences = extract_sentences(clean_text)

    # Compute raw counts
    word_count = len(words)
    # If there are words but no terminating punctuation was used, consider it 1 sentence
    sentence_count = len(sentences) if sentences else (1 if word_count > 0 else 0)

    letter_count = sum(len(re.findall(r"[a-zA-Z]", w)) for w in words)
    character_count = sum(len(c) for c in clean_text if not c.isspace())

    # Syllables and complex words
    word_syllables = [count_syllables_in_word(w) for w in words]
    total_syllables = sum(word_syllables)
    complex_words = sum(
        1 for w, s in zip(words, word_syllables, strict=False) if is_complex_word(w, s)
    )
    unique_words = len({w.lower() for w in words})

    # Descriptive ratios
    avg_words_per_sentence = (
        round(word_count / sentence_count, 2) if sentence_count > 0 else 0.0
    )
    avg_syllables_per_word = (
        round(total_syllables / word_count, 2) if word_count > 0 else 0.0
    )
    avg_letters_per_word = (
        round(letter_count / word_count, 2) if word_count > 0 else 0.0
    )
    complex_word_pct = (
        round((complex_words / word_count) * 100.0, 2) if word_count > 0 else 0.0
    )
    ttr = round(unique_words / word_count, 4) if word_count > 0 else 0.0

    stats = TextStatistics(
        character_count=character_count,
        letter_count=letter_count,
        word_count=word_count,
        sentence_count=sentence_count,
        syllable_count=total_syllables,
        complex_word_count=complex_words,
        unique_word_count=unique_words,
        avg_words_per_sentence=avg_words_per_sentence,
        avg_syllables_per_word=avg_syllables_per_word,
        avg_letters_per_word=avg_letters_per_word,
        complex_word_percentage=complex_word_pct,
        type_token_ratio=ttr,
    )

    # Determine statistical reliability
    is_analyzable = word_count >= 5 and sentence_count >= 1
    reliability: ReliabilityLevel

    if word_count == 0:
        reliability = "unreliable"
        limitations.append("Text contains no recognizable linguistic words.")
    elif word_count < 5:
        reliability = "unreliable"
        limitations.append(
            "Text has fewer than 5 words; insufficient sample size for "
            "statistical formulas."
        )
    elif word_count < 30:
        reliability = "low"
        limitations.append(
            "Short sample (<30 words); statistical variance in readability "
            "formulas is high."
        )
    elif word_count < 100:
        reliability = "medium"
        limitations.append(
            "Sample size between 30 and 100 words; classical formulas were "
            "calibrated on 100+ words."
        )
    else:
        reliability = "high"

    if not is_analyzable:
        # Do not invent scores for insufficient input!
        empty_score = ReadabilityScore(
            score=None,
            grade_level=None,
            interpretation=None,
            description=(
                "Score withheld: text does not satisfy minimum token length "
                "for reliable calculation."
            ),
        )
        return ReadabilityReport(
            is_analyzable=False,
            reliability=reliability,
            language="en",
            statistics=stats,
            flesch_reading_ease=empty_score,
            flesch_kincaid_grade=empty_score,
            gunning_fog=empty_score,
            coleman_liau=empty_score,
            automated_readability_index=empty_score,
            consensus_grade_level=None,
            reading_time_seconds=0.0,
            limitations=limitations,
        )

    # 1. Flesch Reading Ease (0-100 scale, higher is easier)
    # FRE = 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)
    fre_raw = (
        206.835
        - (1.015 * (word_count / sentence_count))
        - (84.6 * (total_syllables / word_count))
    )
    fre_score = round(fre_raw, 2)
    # Estimate equivalent grade level for FRE: ~ (100 - FRE) / 10 + 5
    fre_grade = max(1.0, round((100.0 - fre_score) / 10.0 + 5.0, 1))

    # 2. Flesch-Kincaid Grade Level
    # FKGL = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    fkgl_raw = (
        (0.39 * (word_count / sentence_count))
        + (11.8 * (total_syllables / word_count))
        - 15.59
    )
    fkgl_score = round(max(0.0, fkgl_raw), 2)

    # 3. Gunning Fog Index
    # Fog = 0.4 * ((words / sentences) + 100 * (complex_words / words))
    fog_raw = 0.4 * (
        (word_count / sentence_count) + 100.0 * (complex_words / word_count)
    )
    fog_score = round(max(0.0, fog_raw), 2)

    # 4. Coleman-Liau Index
    # CLI = 0.0588 * L - 0.296 * S - 15.8
    # L = avg letters per 100 words; S = avg sentences per 100 words
    l_val = (letter_count / word_count) * 100.0
    s_val = (sentence_count / word_count) * 100.0
    cli_raw = (0.0588 * l_val) - (0.296 * s_val) - 15.8
    cli_score = round(max(0.0, cli_raw), 2)

    # 5. Automated Readability Index (ARI)
    # ARI = 4.71 * (characters / words) + 0.5 * (words / sentences) - 21.43
    ari_raw = (
        (4.71 * (character_count / word_count))
        + (0.5 * (word_count / sentence_count))
        - 21.43
    )
    ari_score = round(max(0.0, ari_raw), 2)

    # Composite Consensus Grade Level (mean of the 4 grade formulas)
    grade_candidates = [fkgl_score, fog_score, cli_score, ari_score]
    consensus = round(sum(grade_candidates) / len(grade_candidates), 1)

    # Estimated silent reading time: 200 words per minute average reading speed
    reading_time = round((word_count / 200.0) * 60.0, 1)

    return ReadabilityReport(
        is_analyzable=True,
        reliability=reliability,
        language="en",
        statistics=stats,
        flesch_reading_ease=ReadabilityScore(
            score=fre_score,
            grade_level=fre_grade,
            interpretation=interpret_flesch_reading_ease(fre_score),
            description=(
                "Measures readability on a 0-100 scale. "
                "Higher scores indicate easier text."
            ),
        ),
        flesch_kincaid_grade=ReadabilityScore(
            score=fkgl_score,
            grade_level=fkgl_score,
            interpretation=interpret_grade_level(fkgl_score),
            description=(
                "Estimates the US school grade level required to comprehend the text."
            ),
        ),
        gunning_fog=ReadabilityScore(
            score=fog_score,
            grade_level=fog_score,
            interpretation=interpret_grade_level(fog_score),
            description=(
                "Estimates reading grade level based on sentence length and "
                "percentage of 3+ syllable complex words."
            ),
        ),
        coleman_liau=ReadabilityScore(
            score=cli_score,
            grade_level=cli_score,
            interpretation=interpret_grade_level(cli_score),
            description=(
                "Estimates grade level using character and sentence frequencies "
                "without syllable counting."
            ),
        ),
        automated_readability_index=ReadabilityScore(
            score=ari_score,
            grade_level=ari_score,
            interpretation=interpret_grade_level(ari_score),
            description=(
                "Estimates grade level using character counts per word and "
                "words per sentence."
            ),
        ),
        consensus_grade_level=consensus,
        reading_time_seconds=reading_time,
        limitations=limitations,
    )
