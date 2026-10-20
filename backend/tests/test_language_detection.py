"""Tests for the Language Identifier module and API endpoint."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.services.language_detection import (
    SUPPORTED_LANGUAGES,
    LanguageDetectionResult,
    _build_profile,
    _extract_ngrams,
    _normalize_text_for_detection,
    _out_of_place_distance,
    _script_fast_path,
    detect_language,
)

# ---------------------------------------------------------------------------
# Helper: a corpus-length sample for each language
# ---------------------------------------------------------------------------

_SAMPLES = {
    "en": (
        "The quick brown fox jumps over the lazy dog. "
        "Artificial intelligence is transforming the way we live and work. "
        "ReviewPulse is an AI-powered platform that analyzes customer reviews "
        "to help businesses understand their audiences better. "
        "The team is committed to delivering fast, accurate, and reliable insights."
    ),
    "de": (
        "Die schnelle Entwicklung der künstlichen Intelligenz verändert unsere "
        "Gesellschaft grundlegend. Unternehmen setzen zunehmend auf automatisierte "
        "Systeme, um Kundenbewertungen zu analysieren und bessere Entscheidungen "
        "zu treffen. Die Technologie bietet enorme Chancen für die Zukunft."
    ),
    "fr": (
        "L'intelligence artificielle transforme rapidement notre manière de vivre "
        "et de travailler. Les entreprises utilisent de plus en plus des systèmes "
        "automatisés pour analyser les avis des clients et prendre de meilleures "
        "décisions. Cette technologie offre d'énormes opportunités pour l'avenir."
    ),
    "es": (
        "La inteligencia artificial está transformando rápidamente nuestra forma de "
        "vivir y trabajar. Las empresas utilizan cada vez más sistemas automatizados "
        "para analizar las opiniones de los clientes y tomar mejores decisiones. "
        "Esta tecnología ofrece enormes oportunidades para el futuro."
    ),
    "ru": (
        "Искусственный интеллект быстро меняет нашу жизнь и работу. "
        "Компании всё чаще используют автоматизированные системы для анализа "
        "отзывов клиентов и принятия более взвешенных решений. "
        "Эта технология открывает огромные возможности для будущего развития."
    ),
    "ar": (
        "يحوّل الذكاء الاصطناعي حياتنا وعملنا بسرعة كبيرة. "
        "تستخدم الشركات بشكل متزايد الأنظمة الآلية لتحليل آراء العملاء "
        "واتخاذ قرارات أفضل. تقدم هذه التقنية فرصاً هائلة للمستقبل."
    ),
    "zh": (
        "人工智能正在迅速改变我们的生活和工作方式。"
        "企业越来越多地使用自动化系统来分析客户评论并做出更好的决策。"
        "这项技术为未来提供了巨大的机遇和发展空间。"
    ),
    "ja": (
        "人工知能は私たちの生活と仕事を急速に変えています。"
        "企業はますます自動化システムを使用して顧客レビューを分析し、"
        "より良い意思決定を行っています。"
        "この技術は将来に向けて大きな機会を提供しています。"
    ),
}


# ============================================================================
# Unit tests — internal helpers
# ============================================================================


def test_normalize_removes_urls_and_html() -> None:
    raw = "Visit https://example.com or <b>click here</b> for more info."
    norm = _normalize_text_for_detection(raw)
    assert "https" not in norm
    assert "<b>" not in norm
    assert "click here" in norm


def test_extract_ngrams_bigrams() -> None:
    grams = _extract_ngrams("hello", 2)
    assert grams == ["he", "el", "ll", "lo"]


def test_extract_ngrams_trigrams() -> None:
    grams = _extract_ngrams("hello", 3)
    assert grams == ["hel", "ell", "llo"]


def test_build_profile_returns_ranked_dict() -> None:
    profile = _build_profile("aabbaab")
    assert isinstance(profile, dict)
    # "aa" and "ab" should appear; ranks start at 0
    assert all(isinstance(v, int) for v in profile.values())
    # The most frequent gram has rank 0
    most_frequent_rank = min(profile.values())
    assert most_frequent_rank == 0


def test_out_of_place_distance_identical_profile_gives_zero() -> None:
    profile = {"he": 0, "el": 1, "ll": 2, "lo": 3}
    dist = _out_of_place_distance(profile, profile)
    assert dist == 0


def test_out_of_place_distance_missing_grams_penalized() -> None:
    profile = {"zz": 0, "zy": 1}  # grams unlikely in any profile
    lang_table = {"he": 0, "el": 1}
    from app.services.language_detection import _MAX_DISTANCE

    dist = _out_of_place_distance(profile, lang_table)
    assert dist == _MAX_DISTANCE * 2  # both grams absent


def test_script_fast_path_arabic() -> None:
    result = _script_fast_path("مرحبا بالعالم هذا نص عربي طويل")
    assert result == "ar"


def test_script_fast_path_russian() -> None:
    result = _script_fast_path("Привет мир это русский текст для тестирования")
    assert result == "ru"


def test_script_fast_path_japanese() -> None:
    result = _script_fast_path("こんにちは世界これは日本語のテキストです")
    assert result == "ja"


def test_script_fast_path_latin_returns_none() -> None:
    result = _script_fast_path("hello world this is a latin script text")
    assert result is None


# ============================================================================
# Service layer: detect_language() correctness
# ============================================================================


def test_detect_language_too_short_returns_unreliable() -> None:
    result = detect_language("hi")
    assert result.detected_language is None
    assert result.confidence_level == "unreliable"
    assert result.is_reliable is False
    assert result.candidates == []
    assert any("characters" in lim for lim in result.limitations)


def test_detect_language_empty_string_returns_unreliable() -> None:
    result = detect_language("")
    assert result.confidence_level == "unreliable"
    assert result.is_reliable is False


def test_detect_language_english_corpus() -> None:
    result = detect_language(_SAMPLES["en"])
    assert result.detected_language == "en"
    assert result.is_reliable is True
    assert result.confidence > 0.5


def test_detect_language_german_corpus() -> None:
    result = detect_language(_SAMPLES["de"])
    assert result.detected_language == "de"
    assert result.is_reliable is True


def test_detect_language_french_corpus() -> None:
    result = detect_language(_SAMPLES["fr"])
    assert result.detected_language == "fr"
    assert result.is_reliable is True


def test_detect_language_spanish_corpus() -> None:
    result = detect_language(_SAMPLES["es"])
    assert result.detected_language == "es"
    assert result.is_reliable is True


def test_detect_language_russian_script_fast_path() -> None:
    result = detect_language(_SAMPLES["ru"])
    assert result.detected_language == "ru"
    assert result.is_reliable is True
    assert result.script_fast_path is True


def test_detect_language_arabic_script_fast_path() -> None:
    result = detect_language(_SAMPLES["ar"])
    assert result.detected_language == "ar"
    assert result.is_reliable is True
    assert result.script_fast_path is True


def test_detect_language_chinese_script_fast_path() -> None:
    result = detect_language(_SAMPLES["zh"])
    assert result.detected_language == "zh"
    assert result.is_reliable is True
    assert result.script_fast_path is True


def test_detect_language_japanese_script_fast_path() -> None:
    result = detect_language(_SAMPLES["ja"])
    assert result.detected_language == "ja"
    assert result.is_reliable is True
    assert result.script_fast_path is True


def test_detect_language_candidates_ordered_by_rank() -> None:
    result = detect_language(_SAMPLES["en"])
    assert result.candidates[0].rank == 1
    for i, candidate in enumerate(result.candidates):
        assert candidate.rank == i + 1


def test_detect_language_confidence_bounds() -> None:
    result = detect_language(_SAMPLES["fr"])
    assert 0.0 <= result.confidence <= 1.0
    for c in result.candidates:
        assert 0.0 <= c.confidence <= 1.0


def test_detect_language_result_fields() -> None:
    result = detect_language(_SAMPLES["en"])
    assert isinstance(result, LanguageDetectionResult)
    assert result.character_count > 0
    assert isinstance(result.limitations, list)
    assert len(result.limitations) >= 1
    assert result.detected_language_name is not None


def test_detect_language_supported_languages_covered() -> None:
    # Verify the module covers all declared supported languages
    from app.services.language_detection import _PROFILES

    assert set(_PROFILES.keys()) == SUPPORTED_LANGUAGES


# ============================================================================
# API endpoint integration tests
# ============================================================================


def test_api_language_detection_english(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": _SAMPLES["en"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "en"
    assert data["detected_language_name"] == "English"
    assert data["is_reliable"] is True
    assert 0.0 <= data["confidence"] <= 1.0
    assert isinstance(data["candidates"], list)
    assert len(data["candidates"]) > 0
    assert data["candidates"][0]["rank"] == 1


def test_api_language_detection_german(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": _SAMPLES["de"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "de"


def test_api_language_detection_arabic_fast_path(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": _SAMPLES["ar"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] == "ar"
    assert data["script_fast_path"] is True


def test_api_language_detection_short_text_unreliable(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": "hello"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["detected_language"] is None
    assert data["confidence_level"] == "unreliable"
    assert data["is_reliable"] is False


def test_api_language_detection_empty_string_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/language", json={"text": ""})
    assert response.status_code == 422


def test_api_language_detection_whitespace_only_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/language", json={"text": "   \n\t  "})
    assert response.status_code == 422


def test_api_language_detection_missing_body_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/language", json={})
    assert response.status_code == 422


def test_api_language_detection_extra_properties_forbidden(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": _SAMPLES["en"], "unexpected": True},
    )
    assert response.status_code == 422


def test_api_language_detection_response_has_limitations(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/language",
        json={"text": _SAMPLES["en"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["limitations"], list)
    assert len(data["limitations"]) >= 1
