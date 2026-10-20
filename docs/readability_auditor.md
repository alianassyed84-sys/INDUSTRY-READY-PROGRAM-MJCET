# ReviewPulse — Module 707: Readability Auditor Documentation

## 1. Overview

The **Readability Auditor** is an independent, zero-dependency computational linguistics engine designed for ReviewPulse. It analyzes customer reviews, product descriptions, and arbitrary text passages to assess reading difficulty, structural density, and linguistic complexity using classic, peer-reviewed readability formulas.

The module is exposed as a stateless REST endpoint at `POST /api/v1/analysis/readability`.

---

## 2. Supported Metrics & Mathematical Formuals

### 2.1 Flesch Reading Ease (FRE)
- **Reference**: Rudolf Flesch (1948).
- **Purpose**: Assesses comprehension difficulty on a 0–100 scale. Higher scores indicate easier reading.
- **Formula**:
  $$\text{FRE} = 206.835 - 1.015 \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) - 84.6 \left(\frac{\text{Total Syllables}}{\text{Total Words}}\right)$$
- **Score Bands & Interpretation**:
  - `90.0–100.0`: Very Easy (5th grade level; easily understood by an average 10-year-old)
  - `80.0–89.9`: Easy (6th grade level; conversational plain English)
  - `70.0–79.9`: Fairly Easy (7th grade level)
  - `60.0–69.9`: Standard (8th–9th grade level; standard commercial and consumer text)
  - `50.0–59.9`: Fairly Difficult (10th–12th grade level; high school)
  - `30.0–49.9`: Difficult (College academic level)
  - `< 30.0`: Very Confusing (College graduate / professional academic literature)

### 2.2 Flesch-Kincaid Grade Level (FKGL)
- **Reference**: Kincaid, Fishburne, Rogers, & Chissom (1975).
- **Purpose**: Translates structural sentence and syllable density into a direct U.S. school grade level.
- **Formula**:
  $$\text{FKGL} = 0.39 \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) + 11.8 \left(\frac{\text{Total Syllables}}{\text{Total Words}}\right) - 15.59$$
- **Interpretation**: E.g., `8.2` indicates that an 8th-grade student can readily comprehend the passage.

### 2.3 Gunning Fog Index
- **Reference**: Robert Gunning (1952).
- **Purpose**: Estimates reading grade level focusing on complex vocabulary ($\ge 3$ syllables).
- **Formula**:
  $$\text{Fog} = 0.4 \left[ \left(\frac{\text{Total Words}}{\text{Total Sentences}}\right) + 100 \left(\frac{\text{Complex Words}}{\text{Total Words}}\right) \right]$$
- **Complex Words**: Words with 3 or more syllables, excluding standard inflectional suffixes (`-es`, `-ed`, `-ing`) when they do not add root semantic complexity.

### 2.4 Coleman-Liau Index (CLI)
- **Reference**: Meri Coleman & T. L. Liau (1975).
- **Purpose**: Derives grade level using letter and sentence frequencies per 100 words without relying on syllable counting.
- **Formula**:
  $$\text{CLI} = 0.0588 \cdot L - 0.296 \cdot S - 15.8$$
  - $L = \text{Average number of letters per 100 words} = (\text{Letters} / \text{Words}) \times 100$
  - $S = \text{Average number of sentences per 100 words} = (\text{Sentences} / \text{Words}) \times 100$

### 2.5 Automated Readability Index (ARI)
- **Reference**: Senter & Smith (1967).
- **Purpose**: Calculates grade level based on characters per word and words per sentence.
- **Formula**:
  $$\text{ARI} = 4.71 \left(\frac{\text{Characters}}{\text{Words}}\right) + 0.5 \left(\frac{\text{Words}}{\text{Sentences}}\right) - 21.43$$

### 2.6 Consensus Grade Level
The unweighted arithmetic mean across the four school-grade indices (FKGL, Gunning Fog, Coleman-Liau, and ARI) rounded to 1 decimal place, providing a balanced, cross-verified educational requirement.

---

## 3. Assumptions, Statistical Reliability & Limitations

1. **Language Scope**: Calibrated exclusively for modern English (`en`). Applying these metrics to non-English languages will yield mathematically skewed results because syllable distributions, inflection rules, and sentence structures differ fundamentally.
2. **Sample Size & Reliability Classification**:
   - `< 5 words` or `0 sentences`: Marked `is_analyzable: false`, `reliability: "unreliable"`. All formula scores are withheld (`null`). **Scores are never invented for insufficient content.**
   - `5–29 words`: Marked `is_analyzable: true`, `reliability: "low"`. Scores are estimated, but users are cautioned that short samples produce high statistical variance.
   - `30–99 words`: Marked `is_analyzable: true`, `reliability: "medium"`.
   - `≥ 100 words`: Marked `is_analyzable: true`, `reliability: "high"`. Classic formulas were empirically normalized against 100+ word passages.
3. **Sentence Segmentation**: Honors abbreviations (`Dr.`, `Mr.`, `Mrs.`, `U.S.`, `i.e.`, `e.g.`, etc.), single capital initials (`A.`, `B.`), and decimal numbers (`3.14`) without premature sentence splitting.

---

## 4. API Reference

### `POST /api/v1/analysis/readability`

#### Request Payload
- `text` (*string, required*): The text to evaluate ($1 \le \text{length} \le 100{,}000$). Must contain non-whitespace characters.
- Additional unknown fields are rejected (`extra="forbid"`).

#### Example Request
```http
POST /api/v1/analysis/readability HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "text": "ReviewPulse is a product discovery and review intelligence application. It analyzes customer reviews with speed and precision to extract actionable product insights."
}
```

#### Example Response (HTTP 200 OK)
```json
{
  "is_analyzable": true,
  "reliability": "low",
  "language": "en",
  "statistics": {
    "character_count": 142,
    "letter_count": 142,
    "word_count": 22,
    "sentence_count": 2,
    "syllable_count": 45,
    "complex_word_count": 5,
    "unique_word_count": 20,
    "avg_words_per_sentence": 11.0,
    "avg_syllables_per_word": 2.05,
    "avg_letters_per_word": 6.45,
    "complex_word_percentage": 22.73,
    "type_token_ratio": 0.9091
  },
  "flesch_reading_ease": {
    "score": 22.24,
    "grade_level": 12.8,
    "interpretation": "Very Confusing (Graduate level / technical professional prose)",
    "description": "Measures readability on a 0-100 scale. Higher scores indicate easier text."
  },
  "flesch_kincaid_grade": {
    "score": 12.89,
    "grade_level": 12.89,
    "interpretation": "High School (~Grade 13)",
    "description": "Estimates the US school grade level required to comprehend the text."
  },
  "gunning_fog": {
    "score": 13.49,
    "grade_level": 13.49,
    "interpretation": "High School (~Grade 13)",
    "description": "Estimates reading grade level based on sentence length and percentage of 3+ syllable complex words."
  },
  "coleman_liau": {
    "score": 19.45,
    "grade_level": 19.45,
    "interpretation": "Graduate / Professional Degree Level",
    "description": "Estimates grade level using character and sentence frequencies without syllable counting."
  },
  "automated_readability_index": {
    "score": 14.49,
    "grade_level": 14.49,
    "interpretation": "High School (~Grade 14)",
    "description": "Estimates grade level using character counts per word and words per sentence."
  },
  "consensus_grade_level": 15.1,
  "reading_time_seconds": 6.6,
  "limitations": [
    "Calibrated exclusively for English prose (en). Non-English text metrics will not be accurate.",
    "Short sample (<30 words); statistical variance in readability formulas is high."
  ]
}
```

#### Example Insufficient Content Response (HTTP 200 OK)
When text has fewer than 5 words:
```json
{
  "is_analyzable": false,
  "reliability": "unreliable",
  "language": "en",
  "statistics": {
    "character_count": 9,
    "letter_count": 9,
    "word_count": 2,
    "sentence_count": 1,
    "syllable_count": 2,
    "complex_word_count": 0,
    "unique_word_count": 2,
    "avg_words_per_sentence": 2.0,
    "avg_syllables_per_word": 1.0,
    "avg_letters_per_word": 4.5,
    "complex_word_percentage": 0.0,
    "type_token_ratio": 1.0
  },
  "flesch_reading_ease": {
    "score": null,
    "grade_level": null,
    "interpretation": null,
    "description": "Score withheld: text does not satisfy minimum token length for reliable calculation."
  },
  "flesch_kincaid_grade": {
    "score": null,
    "grade_level": null,
    "interpretation": null,
    "description": "Score withheld: text does not satisfy minimum token length for reliable calculation."
  },
  "gunning_fog": {
    "score": null,
    "grade_level": null,
    "interpretation": null,
    "description": "Score withheld: text does not satisfy minimum token length for reliable calculation."
  },
  "coleman_liau": {
    "score": null,
    "grade_level": null,
    "interpretation": null,
    "description": "Score withheld: text does not satisfy minimum token length for reliable calculation."
  },
  "automated_readability_index": {
    "score": null,
    "grade_level": null,
    "interpretation": null,
    "description": "Score withheld: text does not satisfy minimum token length for reliable calculation."
  },
  "consensus_grade_level": null,
  "reading_time_seconds": 0.0,
  "limitations": [
    "Calibrated exclusively for English prose (en). Non-English text metrics will not be accurate.",
    "Text has fewer than 5 words; insufficient sample size for statistical formulas."
  ]
}
```

#### Error Responses
- **HTTP 422 Unprocessable Entity**: When `text` is empty, whitespace-only, missing, or unrecognized fields are provided:
```json
{
  "detail": "Invalid request"
}
```
*(All 422 errors follow ReviewPulse's centralized secure error handler to avoid internal implementation leakage).*
