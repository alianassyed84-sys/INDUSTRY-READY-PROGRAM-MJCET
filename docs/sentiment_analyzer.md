# ReviewPulse — Module 710: Sentiment Analysis & Review Polarity Engine

## 1. Overview

The **Sentiment Analysis Engine** is a zero-dependency, rule- and lexicon-based NLP module designed specifically for consumer product reviews. It computes aggregate sentiment polarity, intensity, proportional components (positive, negative, neutral), and optional **Aspect-Based Sentiment Analysis (ABSA)** for target product attributes.

The module is exposed as a stateless REST endpoint at `POST /api/v1/analysis/sentiment`.

> **Important:** The engine evaluates review text using a calibrated product-review lexicon along with grammatical modifier rules (negation, boosters, capitalization emphasis, punctuation amplification, and contrastive pivots). It executes deterministically in `<1 ms` without external network calls or GPU requirements.

---

## 2. Evaluation Mechanics

### 2.1 Calibrated Lexicon & Baseline Valence
Each known polar token has an assigned valence score on the standard $[-4.0, +4.0]$ scale (similar to AFINN/VADER), calibrated for consumer electronics, appliances, and retail reviews (e.g. `exceptional` $+3.4$, `reliable` $+2.2$, `durable` $+2.3$, `flimsy` $-2.2$, `defective` $-2.5$, `terrible` $-3.4$).

### 2.2 Modifier Rules
When evaluating sentences and clauses:
1. **Negation Tracking:** Negators (`not`, `never`, `hardly`, `barely`, `cannot`, `isn't`, `wasn't`, `without`, etc.) within a 3-token preceding window flip and dampen valence (`adjusted = valence * -0.74`).
2. **Booster Words / Intensifiers:** Amplifiers (`extremely`, `very`, `super`, `really`, `highly`) boost valence intensity; dampeners (`slightly`, `somewhat`, `barely`) reduce intensity.
3. **ALL-CAPS Emphasis:** Uppercase words in mixed-case contexts receive an additional valence boost ($\pm 0.733$).
4. **Exclamation Marks:** Trailing `!` punctuation amplifies clause valence up to $3\times$.
5. **Contrastive Conjunctions:** Conjunctions such as `but`, `however`, `although`, `yet` re-weight clauses: the clause *before* the contrast is dampened ($0.5\times$), while the clause *after* the contrast is prioritized ($1.5\times$).

### 2.3 Compound Score Normalization
The sum of adjusted valence scores $x = \sum v_i$ is squashed into $[-1.0, +1.0]$ via the hyperbolic curve:

$$\text{compound} = \frac{x}{\sqrt{x^2 + \alpha}}, \quad \alpha = 15.0$$

- **Positive:** $\text{compound} \ge 0.05$
- **Negative:** $\text{compound} \le -0.05$
- **Neutral:** $-0.05 < \text{compound} < 0.05$

### 2.4 Aspect-Based Sentiment Analysis (ABSA)
Callers can optionally pass an `aspects` list (e.g. `["battery", "camera", "price", "screen"]`). The engine scans sentence windows for aspect mentions and calculates targeted sentiment scores and extracts snippet context for each aspect.

---

## 3. API Reference

### `POST /api/v1/analysis/sentiment`

#### Request Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `text` | `string` | ✓ | Review text to analyze (1–50,000 characters). |
| `aspects` | `list[string] \| null` | — | Optional list of up to 20 target product aspects to evaluate (each up to 50 characters). |

#### Example Request

```http
POST /api/v1/analysis/sentiment HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json

{
  "text": "The camera is amazing and takes sharp photos! However, the battery life is terrible and dies quickly.",
  "aspects": ["camera", "battery", "display"]
}
```

#### Example Response

```json
{
  "text_length": 104,
  "word_count": 18,
  "scores": {
    "compound": -0.0458,
    "positive": 0.324,
    "negative": 0.338,
    "neutral": 0.338
  },
  "label": "neutral",
  "confidence": 0.246,
  "highlights": [
    {
      "token": "amazing",
      "raw_valence": 3.4,
      "adjusted_valence": 2.1129,
      "modifiers": [
        "exclamations(1)",
        "before_contrast_conjunction"
      ]
    },
    {
      "token": "sharp",
      "raw_valence": 2.1,
      "adjusted_valence": 1.305,
      "modifiers": [
        "exclamations(1)",
        "before_contrast_conjunction"
      ]
    },
    {
      "token": "terrible",
      "raw_valence": -3.4,
      "adjusted_valence": -5.1,
      "modifiers": [
        "after_contrast_conjunction"
      ]
    },
    {
      "token": "dies",
      "raw_valence": -2.3,
      "adjusted_valence": -3.45,
      "modifiers": [
        "after_contrast_conjunction"
      ]
    }
  ],
  "aspects": {
    "camera": {
      "aspect": "camera",
      "compound": 0.7711,
      "label": "positive",
      "mentions_count": 1,
      "snippets": [
        "The camera is amazing and takes sharp photos!"
      ]
    },
    "battery": {
      "aspect": "battery",
      "compound": -0.9105,
      "label": "negative",
      "mentions_count": 1,
      "snippets": [
        "However, the battery life is terrible and dies quickly."
      ]
    },
    "display": {
      "aspect": "display",
      "compound": 0.0,
      "label": "neutral",
      "mentions_count": 0,
      "snippets": []
    }
  },
  "limitations": []
}
```

---

## 4. Limitations & Upgrade Path

- **Lexicon Coverage:** The engine recognizes common English product-review vocabulary. Reviews consisting entirely of slang or domain-specific jargon outside the lexicon will score as neutral, with an explanation in `limitations`.
- **Sarcasm & Irony:** Lexicon methods cannot reliably detect deep sarcasm (e.g. *"Just what I needed, another paperweight"*).
- **Upgrade Path:** For teams requiring transformer embeddings or contextual sarcasm detection, see the `ponytail:` design note in `backend/app/services/sentiment.py` for integrating a fine-tuned RoBERTa model or LLM inference.
