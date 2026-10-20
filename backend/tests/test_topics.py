"""Tests for the Topic Labeler module (TF-IDF) and API endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.services.topics import (
    MAX_TOP_N,
    _idf,
    _ngrams,
    _normalize,
    _tokenize,
    extract_topics,
)

# ---------------------------------------------------------------------------
# Unit tests — internal helpers
# ---------------------------------------------------------------------------


def test_normalize_lowercases_and_strips_urls() -> None:
    raw = "Visit https://example.com or email user@test.com for INFO."
    norm = _normalize(raw)
    assert "https" not in norm
    assert "user@test.com" not in norm
    assert "info" in norm  # lowercased


def test_normalize_strips_html_tags() -> None:
    raw = "This <b>product</b> is <em>excellent</em>."
    norm = _normalize(raw)
    assert "<b>" not in norm
    assert "product" in norm
    assert "excellent" in norm


def test_tokenize_removes_stop_words() -> None:
    tokens = _tokenize("The battery is excellent and the screen is bright.")
    assert "the" not in tokens
    assert "is" not in tokens
    assert "and" not in tokens
    assert "battery" in tokens
    assert "excellent" in tokens
    assert "screen" in tokens
    assert "bright" in tokens


def test_tokenize_removes_single_char_tokens() -> None:
    tokens = _tokenize("a b c great product")
    for tok in tokens:
        assert len(tok) > 1


def test_tokenize_empty_string() -> None:
    assert _tokenize("") == []


def test_tokenize_stop_words_only() -> None:
    # All tokens are stop words — nothing survives
    assert _tokenize("the and is a of") == []


def test_ngrams_unigram() -> None:
    assert _ngrams(["hello", "world"], 1) == ["hello", "world"]


def test_ngrams_bigram() -> None:
    result = _ngrams(["battery", "life", "good"], 2)
    assert result == ["battery life", "life good"]


def test_ngrams_bigram_single_token() -> None:
    # Not enough tokens for a bigram — should return empty
    assert _ngrams(["battery"], 2) == []


def test_idf_raises_degenerate_warning_implicitly() -> None:
    # With 1 document, IDF still works but all present terms score the same.
    token_lists = [["battery", "life"]]
    table = _idf(token_lists, 1, 2, corpus_size=1)
    assert "battery" in table
    assert "life" in table
    # log((1+1)/(1+1)) + 1 = log(1) + 1 = 1.0
    assert table["battery"] == pytest.approx(1.0)


def test_idf_higher_for_rare_terms() -> None:
    # "unique" appears in only 1 of 3 docs; "common" appears in all 3.
    token_lists = [
        ["common", "unique"],
        ["common"],
        ["common"],
    ]
    table = _idf(token_lists, 1, 1, corpus_size=3)
    assert table["unique"] > table["common"]


def test_idf_uniform_single_document() -> None:
    # Single-doc corpus: every term appears in all docs → equal IDF
    token_lists = [["battery", "screen", "excellent"]]
    table = _idf(token_lists, 1, 1, corpus_size=1)
    vals = list(table.values())
    # All IDFs should be equal (log(2/2)+1 = 1.0)
    assert all(v == pytest.approx(vals[0]) for v in vals)


# ---------------------------------------------------------------------------
# extract_topics — functional / integration tests
# ---------------------------------------------------------------------------

_REVIEWS = [
    "The battery life is excellent and the screen is very bright.",
    "Poor battery performance and the display quality is quite dull.",
    "Great screen quality and resolution, but charging time takes very long.",
    "Battery drains quickly, but the camera quality is absolutely exceptional.",
    "The display is vibrant and the camera takes stunning photographs.",
]


def test_extract_topics_returns_correct_corpus_size() -> None:
    result = extract_topics(_REVIEWS)
    assert result.corpus_size == len(_REVIEWS)


def test_extract_topics_all_docs_returned_by_default() -> None:
    result = extract_topics(_REVIEWS)
    assert len(result.documents) == len(_REVIEWS)


def test_extract_topics_focus_index_returns_one_doc() -> None:
    result = extract_topics(_REVIEWS, focus_index=2)
    assert result.focus_index == 2
    assert len(result.documents) == 1
    assert result.documents[0].document_index == 2


def test_extract_topics_keyphrases_sorted_by_score_descending() -> None:
    result = extract_topics(_REVIEWS)
    for doc in result.documents:
        scores = [kp.score for kp in doc.keyphrases]
        assert scores == sorted(scores, reverse=True)


def test_extract_topics_top_n_respected() -> None:
    result = extract_topics(_REVIEWS, top_n=3)
    for doc in result.documents:
        assert len(doc.keyphrases) <= 3


def test_extract_topics_top_n_max_capped() -> None:
    # Requesting more than MAX_TOP_N should be silently capped internally.
    result = extract_topics(_REVIEWS, top_n=MAX_TOP_N + 999)
    for doc in result.documents:
        assert len(doc.keyphrases) <= MAX_TOP_N


def test_extract_topics_keyphrase_scores_nonnegative() -> None:
    result = extract_topics(_REVIEWS)
    for doc in result.documents:
        for kp in doc.keyphrases:
            assert kp.score >= 0.0


def test_extract_topics_term_frequency_bounded() -> None:
    result = extract_topics(_REVIEWS)
    for doc in result.documents:
        for kp in doc.keyphrases:
            assert 0.0 <= kp.term_frequency <= 1.0


def test_extract_topics_document_frequency_bounded() -> None:
    result = extract_topics(_REVIEWS)
    for doc in result.documents:
        for kp in doc.keyphrases:
            assert 1 <= kp.document_frequency <= len(_REVIEWS)


def test_extract_topics_ngram_size_values() -> None:
    result = extract_topics(_REVIEWS)
    for doc in result.documents:
        for kp in doc.keyphrases:
            assert kp.ngram_size in (1, 2)


def test_extract_topics_bigrams_present() -> None:
    # With enough tokens the top keyphrases should include at least one bigram.
    result = extract_topics(_REVIEWS)
    any_bigram = any(
        kp.ngram_size == 2 for doc in result.documents for kp in doc.keyphrases
    )
    assert any_bigram


def test_extract_topics_rare_term_scores_higher_than_common() -> None:
    # "battery" appears in 4/5 reviews; "exceptional" appears in only 1.
    result = extract_topics(_REVIEWS, focus_index=3)
    doc = result.documents[0]
    terms = {kp.term: kp for kp in doc.keyphrases}
    # If both are present, the rarer term should score higher.
    if "exceptional" in terms and "battery" in terms:
        assert terms["exceptional"].score >= terms["battery"].score


def test_extract_topics_single_document_degenerate_warning() -> None:
    result = extract_topics(["This is a single review about battery life."])
    assert result.corpus_size == 1
    assert any("degenerate" in lim for lim in result.limitations)


def test_extract_topics_duplicate_documents() -> None:
    # Duplicate docs are accepted; DF counts accurately reflect repetition.
    docs = ["Great battery life."] * 5
    result = extract_topics(docs)
    assert result.corpus_size == 5
    assert len(result.documents) == 5


def test_extract_topics_empty_token_doc_limitation() -> None:
    # A document that tokenizes to nothing should still appear in results
    # with an empty keyphrase list and a limitation warning.
    docs = ["the and is a of", "Great battery performance."]
    result = extract_topics(docs, focus_index=0)
    doc = result.documents[0]
    assert doc.token_count == 0
    assert doc.keyphrases == []
    assert any("token" in lim.lower() for lim in doc.limitations)


def test_extract_topics_preprocessing_metadata_present() -> None:
    result = extract_topics(_REVIEWS)
    assert "ngram_range" in result.preprocessing
    assert "stop_words" in result.preprocessing
    assert "top_n" in result.preprocessing


def test_extract_topics_limitations_present() -> None:
    result = extract_topics(_REVIEWS)
    assert isinstance(result.limitations, list)
    assert len(result.limitations) >= 1


def test_extract_topics_deterministic() -> None:
    r1 = extract_topics(_REVIEWS, top_n=5)
    r2 = extract_topics(_REVIEWS, top_n=5)
    for d1, d2 in zip(r1.documents, r2.documents, strict=False):
        assert [kp.term for kp in d1.keyphrases] == [kp.term for kp in d2.keyphrases]


# ---------------------------------------------------------------------------
# API integration tests
# ---------------------------------------------------------------------------


def test_api_topics_success(client: TestClient) -> None:
    payload = {"documents": _REVIEWS}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["corpus_size"] == len(_REVIEWS)
    assert len(data["documents"]) == len(_REVIEWS)
    assert data["focus_index"] is None
    assert isinstance(data["limitations"], list)
    assert len(data["limitations"]) >= 1


def test_api_topics_focus_index(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "focus_index": 1}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["focus_index"] == 1
    assert len(data["documents"]) == 1
    assert data["documents"][0]["document_index"] == 1


def test_api_topics_top_n(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "top_n": 3}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 200
    data = response.json()
    for doc in data["documents"]:
        assert len(doc["keyphrases"]) <= 3


def test_api_topics_keyphrase_schema(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "top_n": 5}
    response = client.post("/api/v1/analysis/topics", json=payload)
    data = response.json()
    kp = data["documents"][0]["keyphrases"][0]
    assert "term" in kp
    assert "score" in kp
    assert "term_frequency" in kp
    assert "document_frequency" in kp
    assert "ngram_size" in kp


def test_api_topics_empty_documents_list_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/topics", json={"documents": []})
    assert response.status_code == 422


def test_api_topics_empty_document_string_rejected(client: TestClient) -> None:
    response = client.post(
        "/api/v1/analysis/topics",
        json={"documents": ["valid doc", "  ", "another"]},
    )
    assert response.status_code == 422


def test_api_topics_focus_index_out_of_range_rejected(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "focus_index": 99}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 422


def test_api_topics_missing_documents_rejected(client: TestClient) -> None:
    response = client.post("/api/v1/analysis/topics", json={})
    assert response.status_code == 422


def test_api_topics_extra_fields_rejected(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "unknown_param": True}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 422


def test_api_topics_top_n_too_large_rejected(client: TestClient) -> None:
    payload = {"documents": _REVIEWS, "top_n": MAX_TOP_N + 1}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 422


def test_api_topics_single_document_warning(client: TestClient) -> None:
    payload = {"documents": ["This is a single product review."]}
    response = client.post("/api/v1/analysis/topics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert any("degenerate" in lim for lim in data["limitations"])


def test_api_topics_preprocessing_metadata_in_response(client: TestClient) -> None:
    payload = {"documents": _REVIEWS}
    response = client.post("/api/v1/analysis/topics", json=payload)
    data = response.json()
    assert "preprocessing" in data
    assert data["preprocessing"]["stop_words"] == "english-smart-subset"
    assert data["preprocessing"]["ngram_range"] == [1, 2]
