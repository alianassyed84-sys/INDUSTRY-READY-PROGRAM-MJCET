"""Focused unit tests for Amazon.in product URL validation and ASIN extraction."""

from __future__ import annotations

import pytest

from app.services.harvester.amazon_url import (
    InvalidAmazonUrlError,
    extract_asin_from_path,
    validate_amazon_in_url,
)


class TestValidAmazonUrls:
    """Test valid Amazon India product URLs in various supported formats."""

    def test_standard_dp_url(self) -> None:
        url = "https://www.amazon.in/dp/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"
        assert res.hostname == "www.amazon.in"

    def test_gp_product_url(self) -> None:
        url = "https://www.amazon.in/gp/product/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_slug_with_dp_url(self) -> None:
        url = "https://www.amazon.in/Echo-Dot-4th-Gen/dp/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_slug_with_gp_product_url(self) -> None:
        url = "https://www.amazon.in/Some-Product-Title/gp/product/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"

    def test_mobile_subdomain_and_aw_d_path(self) -> None:
        url = "https://m.amazon.in/gp/aw/d/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.hostname == "m.amazon.in"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_apex_domain_url(self) -> None:
        url = "https://amazon.in/dp/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.hostname == "amazon.in"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_product_path_format(self) -> None:
        url = "https://www.amazon.in/product/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"

    def test_url_with_query_parameters_and_fragment(self) -> None:
        url = (
            "https://www.amazon.in/Echo-Dot/dp/B084J4MZK6"
            "?keywords=echo+dot&qid=1610000000&ref=sr_1_1#customerReviews"
        )
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        # Canonical URL must not contain query parameters or fragments
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_trailing_slash_and_ref_path_segment(self) -> None:
        url = "https://www.amazon.in/dp/B084J4MZK6/ref=cm_cr_arp_d_product_top"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"

    def test_lowercase_asin_normalization(self) -> None:
        url = "https://www.amazon.in/dp/b084j4mzk6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"

    def test_book_isbn10_asin(self) -> None:
        # Books frequently use 10-digit ISBN numbers (all numeric)
        url = "https://www.amazon.in/dp/014345358X"
        res = validate_amazon_in_url(url)
        assert res.asin == "014345358X"


class TestInvalidAmazonUrls:
    """Test rejection of malformed, deceptive, non-HTTPS, or off-domain URLs."""

    def test_reject_http_scheme(self) -> None:
        url = "http://www.amazon.in/dp/B084J4MZK6"
        with pytest.raises(InvalidAmazonUrlError, match="Only secure 'https'"):
            validate_amazon_in_url(url)

    def test_reject_credentials_in_url(self) -> None:
        url = "https://user:secret@www.amazon.in/dp/B084J4MZK6"
        with pytest.raises(InvalidAmazonUrlError, match="embedded credentials"):
            validate_amazon_in_url(url)

    def test_reject_deceptive_hostname_credentials(self) -> None:
        url = "https://amazon.in@attacker.com/dp/B084J4MZK6"
        with pytest.raises(InvalidAmazonUrlError):
            validate_amazon_in_url(url)

    def test_reject_deceptive_subdomain(self) -> None:
        url = "https://amazon.in.attacker.com/dp/B084J4MZK6"
        with pytest.raises(
            InvalidAmazonUrlError, match="Untrusted or unsupported hostname"
        ):
            validate_amazon_in_url(url)

    def test_reject_typosquat_domain(self) -> None:
        url = "https://evilamazon.in/dp/B084J4MZK6"
        with pytest.raises(
            InvalidAmazonUrlError, match="Untrusted or unsupported hostname"
        ):
            validate_amazon_in_url(url)

    def test_reject_other_amazon_locales(self) -> None:
        url = "https://www.amazon.com/dp/B084J4MZK6"
        with pytest.raises(
            InvalidAmazonUrlError, match="Untrusted or unsupported hostname"
        ):
            validate_amazon_in_url(url)

    def test_reject_non_standard_port(self) -> None:
        url = "https://www.amazon.in:8080/dp/B084J4MZK6"
        with pytest.raises(InvalidAmazonUrlError, match="Unsupported port"):
            validate_amazon_in_url(url)

    def test_reject_query_param_only_asin(self) -> None:
        # Query parameters must NOT be trusted as product identifiers
        url = "https://www.amazon.in/search?asin=B084J4MZK6"
        with pytest.raises(
            InvalidAmazonUrlError, match="No recognized Amazon product identifier"
        ):
            validate_amazon_in_url(url)

    def test_reject_missing_identifier_trailing_slash(self) -> None:
        url = "https://www.amazon.in/dp/"
        with pytest.raises(
            InvalidAmazonUrlError, match="No recognized Amazon product identifier"
        ):
            validate_amazon_in_url(url)

    def test_reject_root_url(self) -> None:
        url = "https://www.amazon.in/"
        with pytest.raises(
            InvalidAmazonUrlError, match="No recognized Amazon product identifier"
        ):
            validate_amazon_in_url(url)

    def test_reject_short_asin(self) -> None:
        url = "https://www.amazon.in/dp/B084J"
        with pytest.raises(InvalidAmazonUrlError, match="Malformed ASIN"):
            validate_amazon_in_url(url)

    def test_reject_long_asin(self) -> None:
        url = "https://www.amazon.in/dp/B084J4MZK6EXTRACHARS"
        with pytest.raises(InvalidAmazonUrlError, match="Malformed ASIN"):
            validate_amazon_in_url(url)

    def test_reject_special_characters_in_asin(self) -> None:
        url = "https://www.amazon.in/dp/B084-4MZK!"
        with pytest.raises(InvalidAmazonUrlError, match="Malformed ASIN"):
            validate_amazon_in_url(url)

    @pytest.mark.parametrize("empty_val", ["", "   ", "\t\n"])
    def test_reject_empty_input(self, empty_val: str) -> None:
        with pytest.raises(InvalidAmazonUrlError, match="cannot be empty"):
            validate_amazon_in_url(empty_val)

    def test_reject_ftp_scheme(self) -> None:
        url = "ftp://www.amazon.in/dp/B084J4MZK6"
        with pytest.raises(InvalidAmazonUrlError, match="Only secure 'https'"):
            validate_amazon_in_url(url)

    @pytest.mark.parametrize(
        "bad_input", [None, 42, ["https://www.amazon.in/dp/B084J4MZK6"]]
    )
    def test_reject_non_string_input(self, bad_input: object) -> None:
        with pytest.raises(InvalidAmazonUrlError, match="cannot be empty"):
            validate_amazon_in_url(bad_input)  # type: ignore[arg-type]


class TestValidatedAmazonUrlFields:
    """Test the fields of the ValidatedAmazonUrl result dataclass."""

    def test_raw_url_preserved_after_whitespace_trim(self) -> None:
        padded = "  https://www.amazon.in/dp/B084J4MZK6  "
        res = validate_amazon_in_url(padded)
        assert res.raw_url == "https://www.amazon.in/dp/B084J4MZK6"
        assert res.asin == "B084J4MZK6"

    def test_canonical_url_drops_query_and_fragment(self) -> None:
        url = "https://www.amazon.in/Echo-Dot/dp/B084J4MZK6?ref=sr&tag=foo#reviews"
        res = validate_amazon_in_url(url)
        assert "?" not in res.canonical_url
        assert "#" not in res.canonical_url
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_explicit_port_443_is_accepted(self) -> None:
        url = "https://www.amazon.in:443/dp/B084J4MZK6"
        res = validate_amazon_in_url(url)
        assert res.asin == "B084J4MZK6"
        assert res.canonical_url == "https://www.amazon.in/dp/B084J4MZK6"

    def test_result_is_immutable(self) -> None:
        res = validate_amazon_in_url("https://www.amazon.in/dp/B084J4MZK6")
        with pytest.raises((AttributeError, TypeError)):
            res.asin = "XXXXXXXXXX"  # type: ignore[misc]


class TestExtractAsinFromPath:
    """Unit tests for the public extract_asin_from_path helper."""

    @pytest.mark.parametrize(
        "path, expected",
        [
            ("/dp/B084J4MZK6", "B084J4MZK6"),
            ("/gp/product/B084J4MZK6", "B084J4MZK6"),
            ("/gp/aw/d/B084J4MZK6", "B084J4MZK6"),
            ("/product/B084J4MZK6", "B084J4MZK6"),
            ("/Echo-Dot/dp/B084J4MZK6", "B084J4MZK6"),
            ("/Echo-Dot/gp/product/B084J4MZK6", "B084J4MZK6"),
            ("/dp/B084J4MZK6/ref=sr_1_1", "B084J4MZK6"),
        ],
    )
    def test_recognized_patterns(self, path: str, expected: str) -> None:
        assert extract_asin_from_path(path) == expected

    @pytest.mark.parametrize(
        "path",
        [
            "/",
            "",
            "/about",
            "/dp/",
            "/gp/product/",
            "/search?asin=B084J4MZK6",
        ],
    )
    def test_unrecognized_paths_return_none(self, path: str) -> None:
        assert extract_asin_from_path(path) is None
