"""Pydantic schemas for the Topic Labeler endpoint."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.services.topics import DEFAULT_TOP_N, MAX_CORPUS_DOCS, MAX_DOC_CHARS, MAX_TOP_N


class TopicsRequest(BaseModel):
    """Input payload for TF-IDF keyphrase extraction.

    Provide a ``documents`` list (corpus). To surface keyphrases for a single
    document relative to the rest of the corpus, set ``focus_index`` to that
    document's 0-based position.

    TF-IDF requires a corpus to compute inverse document frequencies. Submitting
    a single document without any reference corpus makes IDF degenerate (all
    terms receive equal weight); the response will include a warning in
    ``limitations``.
    """

    model_config = ConfigDict(extra="forbid")

    documents: list[str] = Field(
        ...,
        min_length=1,
        max_length=MAX_CORPUS_DOCS,
        description=(
            f"List of text documents to analyze (1–{MAX_CORPUS_DOCS} items). "
            "Each document is treated as one row in the TF-IDF corpus."
        ),
        examples=[
            [
                "The battery life is excellent and the screen is bright.",
                "Poor battery performance and the display is dull.",
                "Great screen quality but charging takes too long.",
            ]
        ],
    )
    top_n: int = Field(
        DEFAULT_TOP_N,
        ge=1,
        le=MAX_TOP_N,
        description=(
            f"Maximum number of keyphrases to return per document (1–{MAX_TOP_N})."
        ),
    )
    focus_index: int | None = Field(
        None,
        ge=0,
        description=(
            "If provided, return keyphrases only for the document at this "
            "0-based index. All other documents still contribute to IDF. "
            "If omitted, keyphrases are returned for every document."
        ),
    )

    @field_validator("documents", mode="after")
    @classmethod
    def validate_documents(cls, docs: list[str]) -> list[str]:
        cleaned = []
        for i, doc in enumerate(docs):
            stripped = doc.strip()
            if not stripped:
                raise ValueError(f"Document at index {i} is empty or whitespace-only.")
            if len(stripped) > MAX_DOC_CHARS:
                raise ValueError(
                    f"Document at index {i} exceeds the maximum length of "
                    f"{MAX_DOC_CHARS} characters."
                )
            cleaned.append(stripped)
        return cleaned

    @model_validator(mode="after")
    def validate_focus_index(self) -> TopicsRequest:
        if self.focus_index is not None and self.focus_index >= len(self.documents):
            raise ValueError(
                f"focus_index {self.focus_index} is out of range for a "
                f"corpus of {len(self.documents)} document(s)."
            )
        return self


class KeyphraseSchema(BaseModel):
    """A single ranked keyphrase and its TF-IDF metadata."""

    term: str = Field(..., description="Extracted unigram or bigram keyphrase.")
    score: float = Field(
        ...,
        ge=0.0,
        description="TF-IDF score. Higher means more distinctive in this document.",
    )
    term_frequency: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized term frequency within this document.",
    )
    document_frequency: int = Field(
        ...,
        ge=0,
        description="Number of corpus documents in which this term appears.",
    )
    ngram_size: int = Field(
        ...,
        ge=1,
        description="1 = single word (unigram), 2 = two-word phrase (bigram).",
    )


class DocumentTopicsSchema(BaseModel):
    """Keyphrase extraction result for a single document."""

    document_index: int = Field(
        ..., description="0-based index of the document in the submitted corpus."
    )
    keyphrases: list[KeyphraseSchema] = Field(
        default_factory=list,
        description="Ranked keyphrases, most distinctive first.",
    )
    token_count: int = Field(
        ...,
        description="Number of tokens after preprocessing (stop-word removal, etc.).",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Per-document warnings (e.g., very short document).",
    )


class TopicsResponse(BaseModel):
    """TF-IDF keyphrase extraction response."""

    corpus_size: int = Field(
        ..., description="Number of documents in the submitted corpus."
    )
    focus_index: int | None = Field(
        None,
        description=(
            "The document index for which keyphrases were extracted, or null "
            "if all documents were analyzed."
        ),
    )
    documents: list[DocumentTopicsSchema] = Field(
        default_factory=list,
        description="Per-document keyphrase results.",
    )
    preprocessing: dict[str, object] = Field(
        default_factory=dict,
        description="Preprocessing configuration used for this analysis.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description=(
            "Corpus-level warnings and documented constraints on the analysis."
        ),
    )
