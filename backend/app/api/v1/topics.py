"""Topic labeling endpoint."""

from __future__ import annotations

from dataclasses import asdict

from fastapi import APIRouter, status

from app.schemas.topics import TopicsRequest, TopicsResponse
from app.services.topics import extract_topics

router = APIRouter()


@router.post(
    "/topics",
    response_model=TopicsResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract TF-IDF keyphrases from a corpus of review texts",
    description=(
        "Applies Term Frequency–Inverse Document Frequency (TF-IDF) to a "
        "submitted corpus of documents and returns ranked keyphrases for each "
        "document (or a single focus document). "
        "IDF is computed from the submitted corpus; no external data or "
        "pre-trained model is used. "
        "Supports unigrams and bigrams. "
        "Scores are purely statistical and do not represent semantic meaning."
    ),
)
def label_topics(payload: TopicsRequest) -> TopicsResponse:
    """Analyze a corpus and return TF-IDF ranked keyphrases per document."""
    result = extract_topics(
        payload.documents,
        top_n=payload.top_n,
        focus_index=payload.focus_index,
    )
    data = asdict(result)
    return TopicsResponse.model_validate(data)
