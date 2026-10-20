"""Automated tests for the Readability Auditor module and API endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.services.readability import (
    calculate_readability,
    count_syllables_in_word,
    extract_sentences,
    extract_words,
    is_complex_word,
    normalize_text,
)

# ============================================================================
# Service Layer Unit Tests
# ============================================================================


def test_normalize_text() -> None:
    raw = "  Hello \u00a0 world\u200b! \t "
    normalized = normalize_text(raw)
    assert normalized == "Hello   world!"


def test_sentence_extraction_preserves_abbreviations() -> None:
    text = "Dr. Smith arrived from the U.S. at 5 p.m. He was very tired."
    sentences = extract_sentences(text)
    assert len(sentences) == 2
    assert "Dr. Smith arrived from the U.S. at 5 p.m." in sentences[0]
    assert "He was very tired." in sentences[1]


def test_extract_words_filters_punctuation() -> None:
    text = "ReviewPulse is an AI-powered, state-of-the-art platform! Isn't it great?"
    words = extract_words(text)
    assert "ReviewPulse" in words
    assert "AI-powered" in words
    assert "state-of-the-art" in words
    assert "Isn't" in words
    assert "!" not in words


def test_syllable_counter_heuristics() -> None:
    # Single syllable words
    assert count_syllables_in_word("cat") == 1
    assert count_syllables_in_word("rate") == 1  # silent 'e'
    assert count_syllables_in_word("game") == 1  # silent 'e'
    assert count_syllables_in_word("asked") == 1  # silent '-ed'
    assert count_syllables_in_word("played") == 1  # silent '-ed'

    # Multi-syllable words
    assert count_syllables_in_word("hated") == 2  # '-ed' after 't'
    assert count_syllables_in_word("apple") == 2  # '-le' with consonant
    assert count_syllables_in_word("table") == 2  # '-le' with consonant
    assert count_syllables_in_word("classes") == 2  # '-es' after 's'
    assert count_syllables_in_word("lion") == 2  # 'io' diphthong split
    assert count_syllables_in_word("computer") == 3
    assert count_syllables_in_word("intelligence") == 4


def test_is_complex_word() -> None:
    assert not is_complex_word("cat")
    assert not is_complex_word("simple")
    assert is_complex_word("comprehension")
    assert is_complex_word("methodology")
    assert is_complex_word("extraordinary")


def test_readability_calculation_standard_prose() -> None:
    sample = (
        "The Australian platypus is a unique mammal that lays eggs. "
        "It lives along the eastern coast of Australia in small rivers "
        "and calm streams. "
        "Scientists were confused when they first examined the animal "
        "because it appeared to have the bill of a duck attached to "
        "the body of a beaver. "
        "Today, researchers understand that this creature represents "
        "an early branch of mammalian evolution."
    )
    report = calculate_readability(sample)

    assert report.is_analyzable is True
    assert report.reliability in ("medium", "high")
    assert report.statistics.word_count > 40
    assert report.statistics.sentence_count == 4
    assert report.flesch_reading_ease.score is not None
    assert report.flesch_kincaid_grade.score is not None
    assert report.gunning_fog.score is not None
    assert report.coleman_liau.score is not None
    assert report.automated_readability_index.score is not None
    assert report.consensus_grade_level is not None
    assert report.reading_time_seconds > 0.0
    assert any("English" in lim for lim in report.limitations)


def test_readability_calculation_short_text_withheld() -> None:
    # Fewer than 5 words should not invent scores
    short_text = "Hello world."
    report = calculate_readability(short_text)

    assert report.is_analyzable is False
    assert report.reliability == "unreliable"
    assert report.statistics.word_count == 2
    assert report.flesch_reading_ease.score is None
    assert report.flesch_kincaid_grade.score is None
    assert report.gunning_fog.score is None
    assert report.consensus_grade_level is None
    assert any("fewer than 5 words" in lim for lim in report.limitations)


def test_readability_calculation_empty_and_punctuation() -> None:
    # Empty text
    empty_report = calculate_readability("")
    assert empty_report.is_analyzable is False
    assert empty_report.statistics.word_count == 0
    assert empty_report.flesch_reading_ease.score is None

    # Punctuation only
    punct_report = calculate_readability("!?? ... --- ,,,")
    assert punct_report.is_analyzable is False
    assert punct_report.statistics.word_count == 0
    assert punct_report.flesch_reading_ease.score is None


@pytest.mark.parametrize(
    ("word_count", "expected_level"),
    [
        (2, "unreliable"),
        (10, "low"),
        (40, "medium"),
        (120, "high"),
    ],
)
def test_readability_reliability_levels(word_count: int, expected_level: str) -> None:
    synthetic_words = "The quick brown fox jumps over the lazy dog. " * (
        (word_count // 9) + 1
    )
    words = extract_words(synthetic_words)[:word_count]
    text = " ".join(words) + "."
    report = calculate_readability(text)
    assert report.reliability == expected_level


# ============================================================================
# API Endpoint Integration Tests
# ============================================================================


def test_api_readability_success(client: TestClient) -> None:
    payload = {
        "text": (
            "ReviewPulse processes customer sentiment with speed. "
            "Our automated linguistic analyzer evaluates readability scores "
            "across all user reviews."
        )
    }
    response = client.post("/api/v1/analysis/readability", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["is_analyzable"] is True
    assert data["language"] == "en"
    assert data["statistics"]["word_count"] > 10
    assert data["flesch_reading_ease"]["score"] is not None
    assert isinstance(data["flesch_reading_ease"]["score"], (int, float))
    assert data["flesch_reading_ease"]["interpretation"] is not None
    assert data["consensus_grade_level"] is not None
    assert len(data["limitations"]) >= 1


def test_api_readability_plain_english_standard_score(client: TestClient) -> None:
    payload = {
        "text": (
            "This product is easy to use and works very well for our team. "
            "We were able to set it up in five minutes without any trouble. "
            "The customer service was friendly and helpful whenever we had "
            "questions."
        )
    }
    response = client.post("/api/v1/analysis/readability", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["is_analyzable"] is True
    assert data["flesch_reading_ease"]["score"] > 60.0
    assert (
        "Easy" in data["flesch_reading_ease"]["interpretation"]
        or "Standard" in data["flesch_reading_ease"]["interpretation"]
    )


def test_api_readability_short_text_returns_safe_nulls(
    client: TestClient,
) -> None:
    payload = {"text": "Just fine."}
    response = client.post("/api/v1/analysis/readability", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["is_analyzable"] is False
    assert data["reliability"] == "unreliable"
    assert data["statistics"]["word_count"] == 2
    assert data["flesch_reading_ease"]["score"] is None
    assert data["consensus_grade_level"] is None


def test_api_readability_empty_string_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/readability", json={"text": ""})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_api_readability_whitespace_only_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/readability", json={"text": "   \n\t  "})
    assert response.status_code == 422
    body = response.json()
    assert "detail" in body


def test_api_readability_missing_body_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/readability", json={})
    assert response.status_code == 422


def test_api_readability_extra_properties_forbidden(client: TestClient) -> None:
    payload = {
        "text": "This is valid text for review analysis.",
        "unexpected_param": True,
    }
    response = client.post("/api/v1/analysis/readability", json=payload)
    assert response.status_code == 422
