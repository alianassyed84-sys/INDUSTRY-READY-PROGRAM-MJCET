"""Tests for Module 710: Sentiment Analysis and Review Polarity Engine."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.sentiment import (
    MAX_TEXT_CHARS,
    analyze_sentiment,
)

# ---------------------------------------------------------------------------
# Unit tests: Sentiment Service
# ---------------------------------------------------------------------------


def test_positive_sentiment() -> None:
    text = "The battery life is amazing and the camera is fantastic! Highly recommend."
    result = analyze_sentiment(text)

    assert result.label == "positive"
    assert result.scores.compound > 0.5
    assert result.scores.positive > result.scores.negative
    assert len(result.highlights) >= 3


def test_negative_sentiment() -> None:
    text = (
        "This product is terrible. It arrived broken, completely useless, "
        "and customer support was awful."
    )
    result = analyze_sentiment(text)

    assert result.label == "negative"
    assert result.scores.compound < -0.5
    assert result.scores.negative > result.scores.positive
    assert any(h.token.lower() == "terrible" for h in result.highlights)


def test_neutral_factual_statement() -> None:
    text = "The package arrived on Tuesday. It weighs two kilograms and is rectangular."
    result = analyze_sentiment(text)

    assert result.label == "neutral"
    assert -0.05 <= result.scores.compound <= 0.05
    assert result.scores.neutral > 0.8
    assert len(result.highlights) == 0


def test_negation_inversion() -> None:
    pos_result = analyze_sentiment("The phone is good and reliable.")
    neg_result = analyze_sentiment("The phone is not good and not reliable.")

    assert pos_result.scores.compound > 0.3
    assert neg_result.scores.compound < 0.0
    assert any("negated_by('not')" in h.modifiers for h in neg_result.highlights)


def test_booster_intensifiers() -> None:
    base = analyze_sentiment("The screen is good.")
    boosted = analyze_sentiment("The screen is extremely good.")
    dampened = analyze_sentiment("The screen is slightly good.")

    assert boosted.scores.compound > base.scores.compound
    assert dampened.scores.compound < base.scores.compound
    assert any("boosted_by('extremely')" in h.modifiers for h in boosted.highlights)


def test_all_caps_emphasis() -> None:
    regular = analyze_sentiment("This camera is amazing.")
    caps = analyze_sentiment("This camera is AMAZING.")

    assert caps.scores.compound > regular.scores.compound
    assert any("ALL_CAPS" in h.modifiers for h in caps.highlights)


def test_exclamation_amplification() -> None:
    flat = analyze_sentiment("The quality is great.")
    excited = analyze_sentiment("The quality is great!!!")

    assert excited.scores.compound > flat.scores.compound
    assert any("exclamations(3)" in h.modifiers for h in excited.highlights)


def test_contrastive_conjunction_pivot() -> None:
    # "Great display, but terrible battery" should weight the post-but clause heavier
    text = "Great display, but terrible battery life."
    result = analyze_sentiment(text)

    # Post-but is strongly negative, pre-but is positive
    assert result.label == "negative"
    assert any("after_contrast_conjunction" in h.modifiers for h in result.highlights)
    assert any("before_contrast_conjunction" in h.modifiers for h in result.highlights)


def test_aspect_based_sentiment() -> None:
    text = (
        "The camera takes stunning and beautiful pictures. "
        "However, the battery is terrible and dies within an hour."
    )
    aspects = ["camera", "battery", "display"]
    result = analyze_sentiment(text, aspects=aspects)

    assert "camera" in result.aspects
    assert "battery" in result.aspects
    assert "display" in result.aspects

    assert result.aspects["camera"].label == "positive"
    assert result.aspects["camera"].compound > 0.3
    assert result.aspects["camera"].mentions_count == 1

    assert result.aspects["battery"].label == "negative"
    assert result.aspects["battery"].compound < -0.3
    assert result.aspects["battery"].mentions_count == 1

    assert result.aspects["display"].label == "neutral"
    assert result.aspects["display"].mentions_count == 0


def test_empty_and_whitespace_text() -> None:
    empty = analyze_sentiment("")
    assert empty.label == "neutral"
    assert empty.scores.compound == 0.0
    assert len(empty.limitations) > 0

    spaces = analyze_sentiment("   \n\t  ")
    assert spaces.label == "neutral"
    assert spaces.scores.compound == 0.0


def test_punctuation_only_text() -> None:
    punct = analyze_sentiment("... ??? !!! ---")
    assert punct.label == "neutral"
    assert punct.scores.compound == 0.0
    assert punct.word_count == 0


def test_deterministic_behavior() -> None:
    sample = "Really durable laptop, fast performance, but somewhat pricey."
    r1 = analyze_sentiment(sample)
    r2 = analyze_sentiment(sample)

    assert r1.scores.compound == r2.scores.compound
    assert r1.label == r2.label
    assert len(r1.highlights) == len(r2.highlights)


# ---------------------------------------------------------------------------
# API Integration tests
# ---------------------------------------------------------------------------


def test_sentiment_api_success(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/sentiment",
        json={
            "text": "The keyboard is comfortable and responsive. Love typing on it!",
            "aspects": ["keyboard"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "positive"
    assert data["scores"]["compound"] > 0.4
    assert "keyboard" in data["aspects"]
    assert data["aspects"]["keyboard"]["label"] == "positive"


def test_sentiment_api_validation_empty(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/sentiment",
        json={"text": "   "},
    )
    assert response.status_code == 422


def test_sentiment_api_validation_extra_field(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/sentiment",
        json={"text": "Good phone", "unrecognized": 123},
    )
    assert response.status_code == 422


def test_sentiment_api_aspect_blank(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/sentiment",
        json={"text": "Good phone", "aspects": ["   "]},
    )
    assert response.status_code == 422


def test_sentiment_api_text_too_long(client: TestClient) -> None:
    huge_text = "good " * (MAX_TEXT_CHARS // 4)
    response = client.post(
        "/api/v1/analysis/sentiment",
        json={"text": huge_text},
    )
    assert response.status_code == 422
