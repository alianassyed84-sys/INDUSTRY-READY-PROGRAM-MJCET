"""Tests verifying language detection Unicode block checks, Hinglish detection,
calibrated confidence, and unsupported language handling in sentiment analysis.
"""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event

from app.core.database import Base
from app.models.product import Product
from app.models.review import Review
from app.services.language_detection import detect_language
from app.services.sentiment import analyze_sentiment
from app.services.harvester.insights import compute_product_insights


# ===========================================================================
# 1. Tests for Language Detection (3 samples per language)
# ===========================================================================

class TestLanguageDetectionCoverage:
    """Verifies deterministic script, Hinglish, European, and edge-case detection."""

    # 1. Devanagari (Hindi) - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "यह उत्पाद बहुत अच्छा है और मुझे इसकी गुणवत्ता बहुत पसंद आई।",
            "फोन की बैटरी लाइफ बहुत शानदार है, पूरे दिन आराम से चलती है।",
            "कैमरा क्वालिटी बहुत जबरदस्त है, कम रोशनी में भी बेहतरीन तस्वीरें आती हैं।",
        ],
    )
    def test_devanagari_hindi(self, text: str) -> None:
        # Expected: language 'hi', high confidence, note on Marathi/Nepali in limitations
        res = detect_language(text)
        assert res.detected_language == "hi"
        assert res.is_reliable is True
        assert res.confidence >= 0.90
        assert any("Devanagari" in lim or "Marathi" in lim for lim in res.limitations)

    # 2. Telugu - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "ఈ ఉత్పత్తి చాలా బాగుంది మరియు నేను దీనిని బాగా ఇష్టపడుతున్నాను.",
            "ఫోన్ పనితీరు చాలా వేగంగా ఉంది మరియు కెమెరా స్పష్టత అద్భుతం.",
            "బ్యాటరీ బ్యాకప్ రెండు రోజులు వస్తుంది, చాలా సంతృప్తిగా ఉంది.",
        ],
    )
    def test_telugu(self, text: str) -> None:
        # Expected: language 'te', high confidence
        res = detect_language(text)
        assert res.detected_language == "te"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 3. Tamil - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "இந்த தயாரிப்பு மிகவும் பயனுள்ளது மற்றும் தரமானது.",
            "ஒலி தரம் மிக அருமையாக இருக்கிறது, பேட்டரி நீண்ட நேரம் உழைக்கிறது.",
            "விலைக்கு ஏற்ற சிறந்த தரம், வாங்கியதில் மிக்க மகிழ்ச்சி அடைகிறேன்.",
        ],
    )
    def test_tamil(self, text: str) -> None:
        # Expected: language 'ta', high confidence
        res = detect_language(text)
        assert res.detected_language == "ta"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 4. Bengali - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "এই পণ্যটি সত্যিই খুব ভালো এবং টেকসই, আমি খুব খুশি।",
            "মোবাইলের ক্যামেরা এবং ডিসপ্লে অসাধারণ স্পষ্ট এবং সুন্দর।",
            "দাম অনুযায়ী গুণমান চমৎকার, সবাই নির্দ্বিধায় কিনতে পারেন।",
        ],
    )
    def test_bengali(self, text: str) -> None:
        # Expected: language 'bn', high confidence
        res = detect_language(text)
        assert res.detected_language == "bn"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 5. Gujarati - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "આ પ્રોડક્ટ ખૂબ જ સુંદર અને ઉપયોગી છે, મને બહુ ગમી.",
            "ફોનની સ્પીડ અને બેટરી બંને જોરદાર કામ કરે છે.",
            "ઓછી કિંમતમાં આટલી સારી ક્વોલિટી મળવી મુશ્કેલ છે.",
        ],
    )
    def test_gujarati(self, text: str) -> None:
        # Expected: language 'gu', high confidence
        res = detect_language(text)
        assert res.detected_language == "gu"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 6. Kannada - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "ಈ ಉತ್ಪನ್ನವು ತುಂಬಾ ಉತ್ತಮವಾಗಿದೆ ಮತ್ತು ಗುಣಮಟ್ಟ ಅತ್ಯುತ್ತಮವಾಗಿದೆ.",
            "ಕ್ಯಾಮೆರಾ ಚಿತ್ರಗಳು ಸ್ಪಷ್ಟವಾಗಿವೆ ಮತ್ತು ಧ್ವನಿ ಗುಣಮಟ್ಟ ಚೆನ್ನಾಗಿದೆ.",
            "ಬೆಲೆಗೆ ತಕ್ಕಂತೆ ಉತ್ತಮವಾದ ಫೋನ್, ಎಲ್ಲರಿಗೂ ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ.",
        ],
    )
    def test_kannada(self, text: str) -> None:
        # Expected: language 'kn', high confidence
        res = detect_language(text)
        assert res.detected_language == "kn"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 7. Malayalam - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "ഈ ഉൽപ്പന്നം വളരെ മികച്ചതാണ്, ഉപയോഗിക്കാൻ വളരെ എളുപ്പമാണ്.",
            "ബാറ്ററി ബാക്കപ്പും സൗണ്ട് ക്വാളിറ്റിയും വളരെ മികച്ചതായി തോന്നുന്നു.",
            "വിലയ്ക്ക് അനുയോജ്യമായ നല്ലൊരു ഉൽപ്പന്നം, എനിക്ക് വളരെ ഇഷ്ടപ്പെട്ടു.",
        ],
    )
    def test_malayalam(self, text: str) -> None:
        # Expected: language 'ml', high confidence
        res = detect_language(text)
        assert res.detected_language == "ml"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 8. Gurmukhi (Punjabi) - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "ਇਹ ਉਤਪਾਦ ਬਹੁਤ ਵਧੀਆ ਹੈ ਅਤੇ ਇਸਦੀ ਕੁਆਲਿਟੀ ਸ਼ਾਨਦਾਰ ਹੈ।",
            "ਬੈਟਰੀ ਪੂਰਾ ਦਿਨ ਚੱਲਦੀ ਹੈ ਅਤੇ ਫੋਨ ਦੀ ਆਵਾਜ਼ ਬਹੁਤ ਸਾਫ਼ ਹੈ।",
            "ਮੈਨੂੰ ਇਹ ਸਮਾਨ ਬਹੁਤ ਪਸੰਦ ਆਇਆ, ਪੈਸੇ ਪੂਰੇ ਵਸੂਲ ਹੋ ਗਏ ਹਨ।",
        ],
    )
    def test_gurmukhi_punjabi(self, text: str) -> None:
        # Expected: language 'pa', high confidence
        res = detect_language(text)
        assert res.detected_language == "pa"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 9. Arabic - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "هذا المنتج ممتاز جداً وجودة التصنيع رائعة وأنصح بشرائه بشدة.",
            "البطارية تدوم طويلاً والشاشة واضحة للغاية حتى تحت أشعة الشمس.",
            "خدمة التوصيل كانت سريعة جداً والتغليف ممتاز ومحكم بدون أي تلف.",
        ],
    )
    def test_arabic(self, text: str) -> None:
        # Expected: language 'ar', high confidence
        res = detect_language(text)
        assert res.detected_language == "ar"
        assert res.is_reliable is True
        assert res.confidence >= 0.90

    # 10. Hinglish (hi-Latn) - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "yeh product bahut accha hai aur kaam bhi karta hai ekdum badhiya",
            "battery backup toh bahut kharab hai bilkul bhi nahi chalta",
            "paisa vasool product hai bhai camera aur display dono zabardast hai",
        ],
    )
    def test_hinglish(self, text: str) -> None:
        # Expected: language 'hi-Latn', never 'pt' or 'pl'
        res = detect_language(text)
        assert res.detected_language == "hi-Latn"
        assert res.is_reliable is True
        assert res.confidence >= 0.80

    # 11. English - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "The build quality is exceptional and the battery lasts well over two full days of heavy use.",
            "This product is amazing and I really love using it every single day with my family.",
            "Customer service was prompt and responsive when replacing the defective charger cable.",
        ],
    )
    def test_english(self, text: str) -> None:
        # Expected: language 'en', high confidence
        res = detect_language(text)
        assert res.detected_language == "en"
        assert res.is_reliable is True
        assert res.confidence >= 0.85

    # 12. Spanish - 3 samples
    @pytest.mark.parametrize(
        "text",
        [
            "La calidad de construcción es excelente y la batería dura más de dos días completos sin problemas.",
            "La claridad del sonido es impresionante con graves profundos y sin distorsión alguna al volumen máximo.",
            "El servicio de atención al cliente fue rápido y muy atento al reemplazar el cable defectuoso.",
        ],
    )
    def test_spanish(self, text: str) -> None:
        # Expected: language 'es', high confidence
        res = detect_language(text)
        assert res.detected_language == "es"
        assert res.is_reliable is True
        assert res.confidence >= 0.75

    # 13. Empty & Whitespace
    @pytest.mark.parametrize("text", ["", "   ", "\t\n  \r\n"])
    def test_empty_and_whitespace(self, text: str) -> None:
        # Expected: unreliable / None / unknown
        res = detect_language(text)
        assert res.is_reliable is False
        assert res.detected_language in (None, "unknown")
        assert res.confidence == 0.0

    # 14. Mixed text
    def test_mixed_text_fallback(self) -> None:
        # English sentence with one foreign word or phrase
        text = "The build quality of this Sony bravia model is wonderful and everyone in our family loves it. Sehr gut!"
        res = detect_language(text)
        assert res.detected_language == "en"


# ===========================================================================
# 2. Tests for Calibrated Confidence & Unreliable Guess Handling
# ===========================================================================

class TestConfidenceCalibration:
    """Verifies that confidence is never 1.0 for guesses, and unreliable = unknown."""

    def test_guess_confidence_never_1_0(self) -> None:
        # Random gibberish characters that do not form a clean language match
        gibberish = "qwfp zxcv bnmk lkjh poiuy trewq asdfg"
        res = detect_language(gibberish)
        if not res.is_reliable:
            assert res.detected_language == "unknown"
            assert res.confidence < 1.0


# ===========================================================================
# 3. Tests for Sentiment on Unsupported Non-English Text
# ===========================================================================

class TestSentimentLanguageGating:
    """Verifies non-English text does NOT silently return neutral 0.0."""

    @pytest.mark.parametrize(
        "text, lang_code",
        [
            ("यह फोन बहुत शानदार और टिकाऊ है।", "hi"),
            ("ఈ ఫోన్ చాలా అద్భుతంగా ఉంది.", "te"),
            ("இந்த போன் மிகவும் அருமை.", "ta"),
            ("yeh phone bahut zabardast hai bhai", "hi-Latn"),
            ("Este teléfono es absolutamente fantástico y rápido.", "es"),
        ],
    )
    def test_unsupported_language_returns_explicit_status(self, text: str, lang_code: str) -> None:
        # Must NOT return neutral 0.0 with status supported
        res = analyze_sentiment(text)
        assert res.status == "unsupported_language"
        assert res.label == "unsupported_language"
        assert any("unsupported" in lim.lower() for lim in res.limitations)


# ===========================================================================
# 4. Tests for Aggregated Insights Exclusion in insights.py
# ===========================================================================

@pytest.fixture
async def async_test_session() -> AsyncSession:  # type: ignore[misc]
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_conn, _):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


class TestInsightsLanguageFiltering:
    """Verifies that compute_product_insights excludes unsupported reviews."""

    async def test_insights_excludes_non_english_reviews(self, async_test_session: AsyncSession) -> None:
        prod = Product(
            product_id="TEST_MULTILANG_PROD",
            product_name="Multilingual Test Product",
            category="Electronics",
            rating=4.5,
        )
        async_test_session.add(prod)

        # 2 English positive reviews
        rev1 = Review(
            review_id="rev_en_1",
            product_id=prod.product_id,
            rating=5.0,
            review_title="Amazing battery",
            review_content="The battery life is exceptional and works flawlessly.",
        )
        rev2 = Review(
            review_id="rev_en_2",
            product_id=prod.product_id,
            rating=5.0,
            review_title="Great screen",
            review_content="Super bright display and fantastic build quality.",
        )
        # 2 Non-English reviews (Hindi & Hinglish)
        rev3 = Review(
            review_id="rev_hi_1",
            product_id=prod.product_id,
            rating=5.0,
            review_title="बहुत अच्छा",
            review_content="यह फोन बहुत ही कमाल का है और कैमरा बहुत बढ़िया है।",
        )
        rev4 = Review(
            review_id="rev_hinglish_1",
            product_id=prod.product_id,
            rating=1.0,
            review_title="bekaar product",
            review_content="yeh product bilkul bekaar hai aur paise barbad ho gaye",
        )
        async_test_session.add_all([rev1, rev2, rev3, rev4])
        await async_test_session.commit()

        insights = await compute_product_insights(async_test_session, prod.product_id)
        assert insights is not None

        # Excluded count must be 2 (the Hindi and Hinglish reviews)
        assert insights.sentiment.excluded_unsupported_language_count == 2
        # Total analyzable English reviews should be 2
        assert insights.total_reviews_analyzed == 2
        # Sentiment counts should only count the 2 English positive reviews
        assert insights.sentiment.counts.positive == 2
        assert insights.sentiment.counts.neutral == 0
        assert insights.sentiment.counts.negative == 0
