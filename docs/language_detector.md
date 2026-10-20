# ReviewPulse — Module 708: Language Identifier Documentation

## 1. Overview

The **Language Identifier** is a zero-dependency computational linguistics engine designed for ReviewPulse. It identifies the natural language of customer reviews, submitted text, and product commentary to ensure downstream analysis (such as the English-calibrated Readability Auditor) processes appropriate linguistic content.

The module is exposed as a stateless REST endpoint at `POST /api/v1/analysis/language`.

---

## 2. Detection Methodology & Supported Languages

### 2.1 Supported Languages (ISO 639-1)

| Code | Language | Identification Strategy |
|---|---|---|
| `en` | English | Character n-gram rank-order profiling |
| `de` | German | Character n-gram rank-order profiling |
| `fr` | French | Character n-gram rank-order profiling |
| `es` | Spanish | Character n-gram rank-order profiling |
| `it` | Italian | Character n-gram rank-order profiling |
| `pt` | Portuguese | Character n-gram rank-order profiling |
| `nl` | Dutch | Character n-gram rank-order profiling |
| `pl` | Polish | Character n-gram rank-order profiling |
| `ru` | Russian | Unicode script fast-path (Cyrillic) / n-gram fallback |
| `ar` | Arabic | Unicode script fast-path (Arabic) / n-gram fallback |
| `zh` | Chinese | Unicode script fast-path (CJK Unified Ideographs) / n-gram fallback |
| `ja` | Japanese | Unicode script fast-path (Hiragana/Katakana) / n-gram fallback |

### 2.2 Script-Based Fast-Path
Languages with non-Latin scripts (Arabic, Russian, Japanese, Chinese) are detected with $O(1)$ script density checks:
- Text containing $\ge 25\%$ Arabic script is identified as `ar` with 0.95 confidence.
- Text containing $\ge 25\%$ Cyrillic script is identified as `ru` with 0.95 confidence.
- Text containing $\ge 5\%$ Hiragana or Katakana is identified as `ja` with 0.95 confidence.
- Text containing $\ge 25\%$ Han ideographs without Kana is identified as `zh` with 0.95 confidence.

### 2.3 Character N-Gram Rank-Order Profiling
For Latin-script languages, the engine implements the classic **Cavnar & Trenkle (1994)** algorithm:
1. **Normalization**: Unicode NFKC normalization, URL/HTML stripping, and whitespace folding.
2. **Profile Generation**: Extracts all character bigrams ($n=2$) and trigrams ($n=3$), ranks them by frequency, and selects the top-100 grams.
3. **Out-of-Place Distance Calculation**: Computes rank distance against reference language profiles:
   $$\text{Distance}(D, L) = \sum_{g \in D} \begin{cases} |\text{rank}_D(g) - \text{rank}_L(g)| & \text{if } g \in L \\ \text{MAX\_DISTANCE} (301) & \text{if } g \notin L \end{cases}$$
4. **Confidence Normalization**: Converts raw distances to a $[0.0, 1.0]$ confidence range:
   $$\text{Confidence}(L) = 1.0 - \frac{\text{Distance}(D, L) - \text{BestDistance}}{\text{WorstDistance} - \text{BestDistance}}$$

---

## 3. Statistical Reliability & Limitations

1. **Minimum Sample Size**:
   - `< 20 characters`: Classified as `unreliable`, `detected_language: null`. No score is fabricated for insufficient text.
   - `20–99 characters`: Analysis proceeds, but a cautionary notice is included in `limitations`.
   - `≥ 100 characters`: Recommended sample size for optimal n-gram distribution stability.
2. **Reliability Thresholds**:
   - `is_reliable: true` requires both top candidate confidence $\ge 0.55$ and a candidate separation (margin over the runner-up) $\ge 0.10$.
3. **Domain Scope**: Profiles reflect general prose. Heavy technical jargon, programming code, or mixed multilingual samples may reduce discrimination between closely related languages (such as Spanish and Portuguese).

---

## 4. API Reference

### `POST /api/v1/analysis/language`

#### Request Payload
- `text` (*string, required*): The text to identify ($1 \le \text{length} \le 100{,}000$). Must contain non-whitespace characters.
- Additional unknown fields are rejected (`extra="forbid"`).

#### Example Request
```http
POST /api/v1/analysis/language HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "text": "ReviewPulse is an AI-powered platform that analyzes customer reviews to help businesses understand their audiences better."
}
```

#### Example Response (HTTP 200 OK)
```json
{
  "detected_language": "en",
  "detected_language_name": "English",
  "confidence": 1.0,
  "confidence_level": "high",
  "is_reliable": true,
  "script_fast_path": false,
  "candidates": [
    {
      "language_code": "en",
      "language_name": "English",
      "confidence": 1.0,
      "rank": 1
    },
    {
      "language_code": "nl",
      "language_name": "Dutch",
      "confidence": 0.6053,
      "rank": 2
    }
  ],
  "character_count": 124,
  "analyzed_ngrams": 100,
  "limitations": [
    "Profiles calibrated for general/news-domain text. Domain-specific content, code, or mixed-language input may reduce accuracy.",
    "Minimum recommended input: 20 words / ~100 characters."
  ]
}
```

#### Short / Insufficient Text Response
When text has fewer than 20 characters:
```json
{
  "detected_language": null,
  "detected_language_name": null,
  "confidence": 0.0,
  "confidence_level": "unreliable",
  "is_reliable": false,
  "script_fast_path": false,
  "candidates": [],
  "character_count": 5,
  "analyzed_ngrams": 0,
  "limitations": [
    "Profiles calibrated for general/news-domain text. Domain-specific content, code, or mixed-language input may reduce accuracy.",
    "Minimum recommended input: 20 words / ~100 characters.",
    "Input contains only 5 characters. Fewer than 20 characters is insufficient for reliable detection."
  ]
}
```

#### Error Responses
- **HTTP 422 Unprocessable Entity**: When `text` is empty, whitespace-only, missing, or unrecognized fields are provided.
