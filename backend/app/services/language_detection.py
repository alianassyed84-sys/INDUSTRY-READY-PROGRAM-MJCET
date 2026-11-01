"""Language identification via character n-gram rank-order profiling.

Algorithm: Cavnar & Trenkle (1994) "N-Gram-Based Text Categorization".
Each supported language is represented by a ranked list of its most
frequent character bigrams and trigrams, derived from representative
corpora and hand-verified.  Detection works by:

  1. Extracting bigrams + trigrams from the input text.
  2. Ranking them by frequency.
  3. Computing the sum of rank-position distances against every language
     profile ("out-of-place" distance — lower is a better match).
  4. Converting distances to a 0–1 confidence score.

Supported languages (ISO 639-1):
  en (English), de (German), fr (French), es (Spanish), it (Italian),
  pt (Portuguese), nl (Dutch), pl (Polish), ru (Russian), ar (Arabic),
  zh (Chinese), ja (Japanese)

Limitations:
  - Profiles were derived from general/news-domain text. Domain-specific
    jargon, code, or very short samples may reduce accuracy.
  - Mixed-language input will produce a blend result, not a split.
  - CJK script detection (zh/ja) is primarily character-set based, not
    full gram profiling, and may confuse the two.
  - Minimum recommended input: 20 words / ~100 characters.
  - Script-exclusive languages (Arabic, Russian) are identified with high
    reliability when the script is present.
"""

from __future__ import annotations

import re
import json
from pathlib import Path
import unicodedata
from dataclasses import dataclass
from typing import Final, Literal

# ---------------------------------------------------------------------------
# Type aliases
# ---------------------------------------------------------------------------

LanguageCode = Literal[
    "en",
    "de",
    "fr",
    "es",
    "it",
    "pt",
    "nl",
    "pl",
    "ru",
    "ar",
    "zh",
    "ja",
    "hi",
    "te",
    "ta",
    "bn",
    "gu",
    "kn",
    "ml",
    "pa",
    "hi-Latn",
    "unknown",
]
ConfidenceLevel = Literal["high", "medium", "low", "unreliable"]

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "de": "German",
    "fr": "French",
    "es": "Spanish",
    "it": "Italian",
    "pt": "Portuguese",
    "nl": "Dutch",
    "pl": "Polish",
    "ru": "Russian",
    "ar": "Arabic",
    "zh": "Chinese",
    "ja": "Japanese",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi (Gurmukhi)",
    "hi-Latn": "Hinglish (Latin script)",
    "unknown": "Unknown",
}

SUPPORTED_LANGUAGES: frozenset[str] = frozenset(
    {"en", "de", "fr", "es", "it", "pt", "nl", "pl", "ru", "ar", "zh", "ja"}
)

# Maximum rank distance penalty when a gram is absent from a profile.
_MAX_DISTANCE = 301

# Number of top grams to keep in the input text profile.
_PROFILE_SIZE = 100

# ---------------------------------------------------------------------------
# Language profiles -- top-300 ranked character bigrams + trigrams
# ---------------------------------------------------------------------------

# ponytail: profiles derived from representative corpus text for each language
# using the same _build_profile algorithm. The rank ordering reflects actual
# n-gram frequency distributions, ensuring the scoring is self-consistent.
# A production upgrade would build these from Leipzig Corpora Collection data.
_PROFILES_PATH = Path(__file__).parent / "language_profiles.json"
with open(_PROFILES_PATH, "r", encoding="utf-8") as _f:
    _PROFILES: dict[str, list[str]] = json.load(_f)

_RANK_TABLES: dict[str, dict[str, int]] = {
    lang: {gram: rank for rank, gram in enumerate(grams)}
    for lang, grams in _PROFILES.items()
}

# ---------------------------------------------------------------------------
# Script-based fast-paths for script-exclusive languages & Indic Unicode blocks
# ---------------------------------------------------------------------------

_DEVANAGARI_RE = re.compile(r"[\u0900-\u097f]+")
_BENGALI_RE = re.compile(r"[\u0980-\u09ff]+")
_GURMUKHI_RE = re.compile(r"[\u0a00-\u0a7f]+")
_GUJARATI_RE = re.compile(r"[\u0a80-\u0aff]+")
_TAMIL_RE = re.compile(r"[\u0b80-\u0bff]+")
_TELUGU_RE = re.compile(r"[\u0c00-\u0c7f]+")
_KANNADA_RE = re.compile(r"[\u0c80-\u0cff]+")
_MALAYALAM_RE = re.compile(r"[\u0d00-\u0d7f]+")
_ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+")
_CYRILLIC_RE = re.compile(r"[\u0400-\u04ff]+")
_HIRAGANA_RE = re.compile(r"[\u3040-\u309f]+")
_KATAKANA_RE = re.compile(r"[\u30a0-\u30ff]+")
_HAN_RE = re.compile(r"[\u4e00-\u9fff]+")

# ---------------------------------------------------------------------------
# Hinglish vocabulary & threshold
# ---------------------------------------------------------------------------

HINGLISH_WORDS: Final[frozenset[str]] = frozenset(
    {
        "hai", "hain", "nahi", "nahin", "bahut", "bohot", "accha", "achha",
        "achhi", "acchi", "achhe", "kharab", "mein", "main", "ka", "ke", "ki",
        "ko", "se", "par", "bhi", "aur", "karta", "karti", "karte", "kare",
        "karna", "karne", "hota", "hoti", "hote", "hoga", "hogi", "hogaye",
        "huye", "gaya", "gayi", "gaye", "karo", "kripya", "lekin", "kyun",
        "kyu", "kya", "yeh", "ye", "woh", "wo", "unka", "inka", "mera", "meri",
        "mere", "tera", "teri", "tere", "apna", "apni", "apne", "hum", "tum",
        "aap", "liye", "bhai", "paisa", "vasool", "waala", "wala", "wali",
        "wale", "kuch", "kuchh", "sirf", "sab", "saath", "baad", "pehle",
        "badhiya", "thik", "theek", "yaar", "toh", "bilkul", "chalta",
        "bekaar", "barbad", "dono", "zabardast", "ekdum"
    }
)
HINGLISH_THRESHOLD: Final[int] = 2


def _detect_hinglish(text: str) -> bool:
    """Detect Latin-script text containing common Romanized Hindi vocabulary."""
    tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if not tokens:
        return False
    matched = {w for w in tokens if w in HINGLISH_WORDS}
    return len(matched) >= HINGLISH_THRESHOLD


def _script_fast_path(text: str) -> str | None:
    """Return language_code if a dominant script uniquely identifies it."""
    # Count non-whitespace characters for fair density evaluation
    non_space = [c for c in text if not c.isspace()]
    total = max(len(non_space), 1)

    devanagari = len("".join(_DEVANAGARI_RE.findall(text))) / total
    telugu = len("".join(_TELUGU_RE.findall(text))) / total
    tamil = len("".join(_TAMIL_RE.findall(text))) / total
    bengali = len("".join(_BENGALI_RE.findall(text))) / total
    gujarati = len("".join(_GUJARATI_RE.findall(text))) / total
    kannada = len("".join(_KANNADA_RE.findall(text))) / total
    malayalam = len("".join(_MALAYALAM_RE.findall(text))) / total
    gurmukhi = len("".join(_GURMUKHI_RE.findall(text))) / total

    arabic = len("".join(_ARABIC_RE.findall(text))) / total
    cyrillic = len("".join(_CYRILLIC_RE.findall(text))) / total
    hiragana = len("".join(_HIRAGANA_RE.findall(text))) / total
    katakana = len("".join(_KATAKANA_RE.findall(text))) / total
    han = len("".join(_HAN_RE.findall(text))) / total

    if devanagari > 0.15:
        return "hi"
    if telugu > 0.15:
        return "te"
    if tamil > 0.15:
        return "ta"
    if bengali > 0.15:
        return "bn"
    if gujarati > 0.15:
        return "gu"
    if kannada > 0.15:
        return "kn"
    if malayalam > 0.15:
        return "ml"
    if gurmukhi > 0.15:
        return "pa"
    if arabic > 0.15:
        return "ar"
    if cyrillic > 0.15:
        return "ru"
    if hiragana > 0.05 or katakana > 0.05:
        return "ja"
    if han > 0.15:
        return "zh"

    return None


# ---------------------------------------------------------------------------
# Core n-gram engine
# ---------------------------------------------------------------------------


def _extract_ngrams(text: str, n: int) -> list[str]:
    """Return all character n-grams of length n from text."""
    return [text[i : i + n] for i in range(len(text) - n + 1)]


def _build_profile(text: str, size: int = _PROFILE_SIZE) -> dict[str, int]:
    """Build a ranked {gram: rank} profile from the top-N grams in text."""
    freq: dict[str, int] = {}
    for gram in _extract_ngrams(text, 2) + _extract_ngrams(text, 3):
        freq[gram] = freq.get(gram, 0) + 1
    ranked = sorted(freq, key=lambda g: freq[g], reverse=True)[:size]
    return {gram: rank for rank, gram in enumerate(ranked)}


def _out_of_place_distance(
    input_profile: dict[str, int], lang_table: dict[str, int]
) -> int:
    """Compute sum of rank-position distances (lower = better match).

    For each gram in the input profile:
    - If present in the language profile: abs(input_rank - lang_rank)
    - If absent: _MAX_DISTANCE (penalty)
    """
    total = 0
    for gram, input_rank in input_profile.items():
        lang_rank = lang_table.get(gram)
        if lang_rank is None:
            total += _MAX_DISTANCE
        else:
            total += abs(input_rank - lang_rank)
    return total


def _normalize_text_for_detection(text: str) -> str:
    """Lowercase and strip irrelevant content; preserve script chars."""
    normalized = unicodedata.normalize("NFKC", text)
    # Remove URLs and email addresses
    normalized = re.sub(r"https?://\S+|www\.\S+|\S+@\S+\.\S+", " ", normalized)
    # Remove HTML tags
    normalized = re.sub(r"<[^>]+>", " ", normalized)
    # Collapse all whitespace (tabs, newlines, multiple spaces) to single space
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.lower().strip()


# ---------------------------------------------------------------------------
# Public data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LanguageCandidate:
    """Individual language candidate with its confidence score."""

    language_code: str
    language_name: str
    confidence: float  # 0.0-1.0 (higher is better)
    rank: int  # 1 = best match


@dataclass(frozen=True)
class LanguageDetectionResult:
    """Result of character n-gram language identification."""

    detected_language: str | None
    detected_language_name: str | None
    confidence: float
    confidence_level: ConfidenceLevel
    is_reliable: bool
    script_fast_path: bool
    candidates: list[LanguageCandidate]
    character_count: int
    analyzed_ngrams: int
    limitations: list[str]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_MIN_CHARS = 20
_HIGH_CONF = 0.80
_MEDIUM_CONF = 0.55
_LOW_CONF = 0.30


def detect_language(text: str) -> LanguageDetectionResult:
    """Identify the most likely language of input text.

    Args:
        text: Raw text string to analyze.

    Returns:
        LanguageDetectionResult with ranked candidates, confidence, and metadata.
    """
    normalized = _normalize_text_for_detection(text)
    char_count = len(normalized.strip())
    limitations: list[str] = [
        "Profiles calibrated for general/news-domain text. Domain-specific "
        "content, code, or mixed-language input may reduce accuracy.",
        "Minimum recommended input: 20 words / ~100 characters.",
    ]

    if char_count < _MIN_CHARS:
        limitations.append(
            f"Input contains only {char_count} characters. "
            "Fewer than 20 characters is insufficient for reliable detection."
        )
        return LanguageDetectionResult(
            detected_language=None,
            detected_language_name=None,
            confidence=0.0,
            confidence_level="unreliable",
            is_reliable=False,
            script_fast_path=False,
            candidates=[],
            character_count=char_count,
            analyzed_ngrams=0,
            limitations=limitations,
        )

    fast_lang = _script_fast_path(normalized)
    if fast_lang:
        if fast_lang == "hi":
            limitations.append(
                "Devanagari script detected: classified as Hindi ('hi'); note that Marathi and Nepali also share Devanagari script."
            )
        name = LANGUAGE_NAMES[fast_lang]
        return LanguageDetectionResult(
            detected_language=fast_lang,
            detected_language_name=name,
            confidence=0.98,
            confidence_level="high",
            is_reliable=True,
            script_fast_path=True,
            candidates=[
                LanguageCandidate(
                    language_code=fast_lang,
                    language_name=name,
                    confidence=0.98,
                    rank=1,
                )
            ],
            character_count=char_count,
            analyzed_ngrams=0,
            limitations=limitations,
        )

    if _detect_hinglish(normalized):
        hinglish_code = "hi-Latn"
        hinglish_name = LANGUAGE_NAMES[hinglish_code]
        limitations.append(
            "Hinglish detected via Romanized Hindi vocabulary in Latin script."
        )
        return LanguageDetectionResult(
            detected_language=hinglish_code,
            detected_language_name=hinglish_name,
            confidence=0.95,
            confidence_level="high",
            is_reliable=True,
            script_fast_path=True,
            candidates=[
                LanguageCandidate(
                    language_code=hinglish_code,
                    language_name=hinglish_name,
                    confidence=0.95,
                    rank=1,
                )
            ],
            character_count=char_count,
            analyzed_ngrams=0,
            limitations=limitations,
        )

    input_profile = _build_profile(normalized)
    ngram_count = len(input_profile)

    scores: dict[str, int] = {
        lang: _out_of_place_distance(input_profile, table)
        for lang, table in _RANK_TABLES.items()
    }

    ranked = sorted(scores.items(), key=lambda kv: kv[1])

    best_dist = ranked[0][1]
    worst_dist = ranked[-1][1]
    dist_range = max(worst_dist - best_dist, 1)

    # Statistical rank n-gram profiling is an approximation (a guess).
    # Rule 3: Confidence must NEVER be 1.0 for a guess.
    _MAX_GUESS_CONF = 0.95

    def _to_confidence(dist: int) -> float:
        return round(_MAX_GUESS_CONF * (1.0 - (dist - best_dist) / dist_range), 4)

    candidates = [
        LanguageCandidate(
            language_code=lang,
            language_name=LANGUAGE_NAMES[lang],
            confidence=_to_confidence(dist),
            rank=i + 1,
        )
        for i, (lang, dist) in enumerate(ranked)
    ]

    top_conf = candidates[0].confidence
    second_conf = candidates[1].confidence if len(candidates) > 1 else 0.0
    separation = top_conf - second_conf

    # Reliable if medium confidence and clear separation between candidates
    is_reliable = top_conf >= _MEDIUM_CONF and separation >= 0.10

    if is_reliable:
        if top_conf >= _HIGH_CONF:
            conf_level: ConfidenceLevel = "high"
        elif top_conf >= _MEDIUM_CONF:
            conf_level = "medium"
        else:
            conf_level = "low"
        detected_lang: str | None = candidates[0].language_code
        detected_name: str | None = candidates[0].language_name
    else:
        conf_level = "unreliable"
        # Rule 3: If is_reliable is False, the result must say language unknown.
        detected_lang = "unknown"
        detected_name = "Unknown"
        top_conf = min(top_conf, 0.49)
        limitations.append(
            "Confidence is low or text did not match any supported language profile cleanly. "
            "Language classified as unknown."
        )

    if char_count < 100:
        limitations.append(
            f"Only {char_count} characters analyzed. "
            "Results improve significantly with 100+ characters."
        )

    return LanguageDetectionResult(
        detected_language=detected_lang,
        detected_language_name=detected_name,
        confidence=top_conf,
        confidence_level=conf_level,
        is_reliable=is_reliable,
        script_fast_path=False,
        candidates=candidates,
        character_count=char_count,
        analyzed_ngrams=ngram_count,
        limitations=limitations,
    )
