"""Pydantic schemas for the Sentiment Analysis endpoint."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.sentiment import MAX_ASPECT_CHARS, MAX_ASPECTS, MAX_TEXT_CHARS


class SentimentRequest(BaseModel):
    """Input payload for sentiment analysis."""

    model_config = ConfigDict(extra="forbid")

    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_TEXT_CHARS,
        description=f"Review text to analyze (1–{MAX_TEXT_CHARS} characters).",
        examples=[
            "The battery life is amazing and the camera is fantastic, "
            "but customer service was terrible."
        ],
    )
    aspects: list[str] | None = Field(
        None,
        max_length=MAX_ASPECTS,
        description=(
            f"Optional list of target product attributes/aspects to evaluate "
            f"(up to {MAX_ASPECTS} aspects, e.g. ['battery', 'camera', 'price'])."
        ),
        examples=[["battery", "camera", "customer service"]],
    )

    @field_validator("text", mode="after")
    @classmethod
    def validate_text_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Review text must not be empty or purely whitespace.")
        return v

    @field_validator("aspects", mode="after")
    @classmethod
    def validate_aspects(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return None
        cleaned: list[str] = []
        for aspect in v:
            clean_item = aspect.strip()
            if not clean_item:
                raise ValueError("Aspect strings cannot be empty or purely whitespace.")
            if len(clean_item) > MAX_ASPECT_CHARS:
                raise ValueError(
                    f"Aspect '{clean_item[:20]}...' exceeds maximum length of "
                    f"{MAX_ASPECT_CHARS} characters."
                )
            cleaned.append(clean_item)
        return cleaned


class PolarHighlightSchema(BaseModel):
    """A polar token in the text that influenced the sentiment score."""

    model_config = ConfigDict(extra="forbid")

    token: str = Field(..., description="The matched word or token in the review text.")
    raw_valence: float = Field(
        ..., description="Baseline dictionary valence rating [-4.0 to +4.0]."
    )
    adjusted_valence: float = Field(
        ...,
        description=(
            "Valence after modifiers (negation, boosters, ALL-CAPS, "
            "punctuation, clause)."
        ),
    )
    modifiers: list[str] = Field(
        default_factory=list,
        description=(
            "List of modifier rules applied (e.g. 'negated_by(not)', 'ALL_CAPS')."
        ),
    )


class AspectSentimentSchema(BaseModel):
    """Aspect-specific sentiment measurement."""

    model_config = ConfigDict(extra="forbid")

    aspect: str = Field(..., description="The product attribute/aspect evaluated.")
    compound: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description="Aspect-targeted compound sentiment score [-1.0, +1.0].",
    )
    label: str = Field(
        ...,
        pattern="^(positive|negative|neutral)$",
        description=(
            "Sentiment category for this aspect: 'positive', 'negative', or 'neutral'."
        ),
    )
    mentions_count: int = Field(
        ..., ge=0, description="Number of sentences mentioning this aspect."
    )
    snippets: list[str] = Field(
        default_factory=list,
        description="Relevant review sentences mentioning this aspect.",
    )


class SentimentScoresSchema(BaseModel):
    """Breakdown of sentiment scores."""

    model_config = ConfigDict(extra="forbid")

    compound: float = Field(
        ...,
        ge=-1.0,
        le=1.0,
        description=(
            "Normalized aggregate sentiment score bounded between -1.0 (most negative) "
            "and +1.0 (most positive)."
        ),
    )
    positive: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized proportion of positive valence tokens [0.0, 1.0].",
    )
    negative: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized proportion of negative valence tokens [0.0, 1.0].",
    )
    neutral: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Normalized proportion of neutral words [0.0, 1.0].",
    )


class SentimentResponse(BaseModel):
    """Output payload for the sentiment analysis endpoint."""

    model_config = ConfigDict(extra="forbid")

    text_length: int = Field(
        ..., ge=0, description="Total characters in the input review."
    )
    word_count: int = Field(..., ge=0, description="Total word tokens detected.")
    scores: SentimentScoresSchema = Field(
        ..., description="Overall sentiment score breakdown."
    )
    label: str = Field(
        ...,
        pattern="^(positive|negative|neutral)$",
        description=(
            "Primary sentiment polarity classification: "
            "'positive', 'negative', or 'neutral'."
        ),
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Estimated confidence score in the categorical classification [0.0, 1.0]."
        ),
    )
    highlights: list[PolarHighlightSchema] = Field(
        default_factory=list,
        description=(
            "Key polar terms that drove the sentiment calculation, "
            "with active modifiers."
        ),
    )
    aspects: dict[str, AspectSentimentSchema] = Field(
        default_factory=dict,
        description="Sentiment breakdown for each specified aspect target.",
    )
    limitations: list[str] = Field(
        default_factory=list,
        description="Applicable disclaimers or edge-case notes for this review.",
    )
