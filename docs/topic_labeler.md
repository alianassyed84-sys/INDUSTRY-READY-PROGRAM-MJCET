# ReviewPulse — Module 709: Topic Labeler (TF-IDF Keyphrase Extraction)

## 1. Overview

The **Topic Labeler** is a zero-dependency keyphrase extraction engine for ReviewPulse. It applies **TF-IDF (Term Frequency–Inverse Document Frequency)** to a caller-supplied corpus of review texts and returns ranked keyphrases (unigrams and bigrams) for each document.

The module is exposed as a stateless REST endpoint at `POST /api/v1/analysis/topics`.

> **Important:** TF-IDF is a statistical ranking method. Keyphrases reflect *term distinctiveness within the submitted corpus*, not semantic topics, sentiment, or intent. The engine does not call any external service or transmit data to third parties.

---

## 2. How TF-IDF Works Here

### 2.1 Corpus Requirement

TF-IDF requires a **corpus** (multiple documents) to compute meaningful Inverse Document Frequency (IDF) weights. The IDF of a term measures how rare it is across the corpus:

$$\text{IDF}(t) = \log\!\left(\frac{1 + N}{1 + \text{df}(t)}\right) + 1$$

where $N$ is the corpus size and $\text{df}(t)$ is the number of documents containing term $t$. The smoothing formula (sklearn-style) prevents division by zero and ensures unseen terms still receive a score.

Submitting a single document makes IDF degenerate (all terms score equally); the response includes a warning in `limitations`.

### 2.2 TF-IDF Score

$$\text{TF-IDF}(t, d) = \frac{\text{count}(t, d)}{\text{total\_terms}(d)} \times \text{IDF}(t)$$

Higher scores indicate terms that appear frequently in a specific document *and* rarely across the rest of the corpus — the most distinctive terms.

### 2.3 N-gram Extraction

Both **unigrams** (single words) and **bigrams** (two-word phrases) are extracted. Bigrams often capture more meaningful phrases than individual words (e.g. "battery life" rather than "battery" and "life" separately).

### 2.4 Preprocessing Pipeline

| Step | Detail |
|---|---|
| Unicode normalization | NFKC (handles ligatures, fullwidth characters) |
| URL/email stripping | Removed before tokenization |
| HTML tag stripping | `<tag>` patterns removed |
| Lowercasing | All text lowercased |
| Tokenization | `[a-z]+(?:['-][a-z]+)*` — alphabetic only, hyphens/apostrophes preserved |
| Stop-word removal | English-only subset of SMART stop-word list (~100 words) |
| Min token length | 2 characters (single letters dropped) |

---

## 3. API Reference

### `POST /api/v1/analysis/topics`

#### Request Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `documents` | `list[string]` | ✓ | 1–500 document strings. Each up to 50,000 characters. |
| `top_n` | `integer` | — | Max keyphrases per document (1–50, default 10). |
| `focus_index` | `integer \| null` | — | 0-based index of the document to focus on. Other docs still contribute to IDF. If omitted, all docs are scored. |

#### Example: Corpus analysis (all documents)

```http
POST /api/v1/analysis/topics HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "documents": [
    "The battery life is excellent and the screen is very bright.",
    "Poor battery performance and the display quality is quite dull.",
    "Great screen quality and resolution, but charging time takes very long."
  ],
  "top_n": 5
}
```

#### Example: Focus on one document

```json
{
  "documents": [
    "The battery life is excellent and the screen is very bright.",
    "Poor battery performance and the display quality is quite dull.",
    "Great screen quality and resolution, but charging time takes very long."
  ],
  "top_n": 5,
  "focus_index": 2
}
```

With `focus_index: 2`, only document 2 ("Great screen quality...") is scored. Documents 0 and 1 still contribute to IDF, so "screen" gets a lower IDF because it appears in doc 0 and 2, while "charging" (unique to doc 2) scores higher.

#### Example Response (HTTP 200 OK)

```json
{
  "corpus_size": 3,
  "focus_index": null,
  "documents": [
    {
      "document_index": 0,
      "keyphrases": [
        {
          "term": "battery life",
          "score": 0.127451,
          "term_frequency": 0.090909,
          "document_frequency": 1,
          "ngram_size": 2
        },
        {
          "term": "excellent",
          "score": 0.127451,
          "term_frequency": 0.090909,
          "document_frequency": 1,
          "ngram_size": 1
        }
      ],
      "token_count": 7,
      "limitations": []
    }
  ],
  "preprocessing": {
    "ngram_range": [1, 2],
    "stop_words": "english-smart-subset",
    "normalization": "NFKC-lowercase-url-html-strip",
    "min_token_length": 2,
    "top_n": 5
  },
  "limitations": [
    "TF-IDF is a statistical ranking method. Scores reflect term distinctiveness within this corpus, not semantic meaning or topics.",
    "Stop-word filtering is English-only. Documents in other languages will include function words in their keyphrase lists."
  ]
}
```

#### Error Responses
- **HTTP 422**: Empty document list, whitespace-only document, `focus_index` out of range, `top_n` outside 1–50, extra fields, missing `documents`.

---

## 4. Corpus Versioning & Reuse

**Model fitting is explicit and per-request.** There is no hidden background corpus or pre-fitted vectorizer. Every call to `POST /api/v1/analysis/topics` fits IDF from the submitted `documents` list.

This means:
- The same text can produce different keyphrase scores if the surrounding corpus changes.
- Callers must send a representative and stable corpus to get comparable scores across calls.

**When to use a pre-fitted vectorizer (upgrade path):**  
If you process >1,000 documents repeatedly with the same reference corpus, cache the IDF table keyed on a deterministic fingerprint (e.g. SHA-256 of sorted document hashes) and store it in FastAPI app state. The `ponytail` comment in `services/topics.py` documents this ceiling explicitly.

---

## 5. Limitations

1. **Statistical, not semantic.** TF-IDF does not understand meaning. "excellent" and "outstanding" are completely different terms with independent scores.
2. **English stop words only.** Non-English documents will include their grammatical function words in keyphrases.
3. **No stemming or lemmatization.** "battery" and "batteries" are different terms. This is intentional and explicit.
4. **Corpus sensitivity.** A single document or a highly uniform corpus (all reviews mention "battery") reduces discriminative power.
5. **Bigram adjacency.** Bigrams are formed from adjacent tokens *after* stop-word removal. "battery very life" → after removing "very" → "battery life" (bigram). This can produce unexpected pairings.
6. **Input size.** Maximum 500 documents per request, 50,000 characters per document.

---

## 6. Files

| File | Purpose |
|---|---|
| `backend/app/services/topics.py` | TF-IDF engine (stdlib only: `math`, `re`, `collections`, `unicodedata`) |
| `backend/app/schemas/topics.py` | Pydantic request/response schemas |
| `backend/app/api/v1/topics.py` | FastAPI endpoint |
| `backend/tests/test_topics.py` | 42 automated tests |
