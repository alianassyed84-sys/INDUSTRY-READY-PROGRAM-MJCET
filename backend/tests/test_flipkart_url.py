"""Tests for Flipkart product URL validation and PID extraction."""

import pytest

from app.services.harvester.flipkart_url import (
    InvalidFlipkartUrlError,
    extract_title_hint_from_path,
    validate_flipkart_url,
)


def test_validate_valid_flipkart_product_url() -> None:
    url = (
        "https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
        "?pid=MOBGTAGPNRQA7CS3&lid=LSTMOD"
    )
    res = validate_flipkart_url(url)
    assert res.pid == "MOBGTAGPNRQA7CS3"
    assert res.hostname == "www.flipkart.com"
    assert "pid=MOBGTAGPNRQA7CS3" in res.canonical_url
    assert res.title_hint == "Apple Iphone 15 Black 128 Gb"


def test_validate_valid_flipkart_reviews_url() -> None:
    url = (
        "https://www.flipkart.com/product-reviews/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4"
        "?pid=MOBGTAGPNRQA7CS3"
    )
    res = validate_flipkart_url(url)
    assert res.pid == "MOBGTAGPNRQA7CS3"
    assert res.title_hint == "Apple Iphone 15 Black 128 Gb"


def test_validate_bare_domain_and_mobile_host() -> None:
    res1 = validate_flipkart_url("https://flipkart.com/p/itm123?pid=MOBGTAGPNRQA7CS3")
    assert res1.pid == "MOBGTAGPNRQA7CS3"

    res2 = validate_flipkart_url("https://dl.flipkart.com/dl/p/itm123?pid=MOBGTAGPNRQA7CS3")
    assert res2.pid == "MOBGTAGPNRQA7CS3"


def test_reject_insecure_scheme() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="Only secure 'https' URLs are accepted"):
        validate_flipkart_url("http://www.flipkart.com/product/p/itm?pid=MOBGTAGPNRQA7CS3")


def test_reject_embedded_credentials() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="embedded credentials are forbidden"):
        validate_flipkart_url("https://admin:pass@www.flipkart.com/p/itm?pid=MOBGTAGPNRQA7CS3")


def test_reject_untrusted_domain() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="Untrusted or unsupported hostname"):
        validate_flipkart_url("https://www.amazon.in/dp/B084J4MZK6?pid=MOBGTAGPNRQA7CS3")

    with pytest.raises(InvalidFlipkartUrlError, match="Untrusted or unsupported hostname"):
        validate_flipkart_url("https://flipkart.phishing.com/p/itm?pid=MOBGTAGPNRQA7CS3")


def test_reject_missing_or_empty_pid() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="Missing 'pid' query parameter"):
        validate_flipkart_url("https://www.flipkart.com/apple-iphone-15-black-128-gb/p/itm6ac6485515ae4")

    with pytest.raises(InvalidFlipkartUrlError, match="Missing 'pid' query parameter"):
        validate_flipkart_url("https://www.flipkart.com/p/itm?pid=")


def test_reject_malformed_pid() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="Malformed Flipkart PID"):
        validate_flipkart_url("https://www.flipkart.com/p/itm?pid=AB")  # Too short


def test_reject_empty_and_whitespace_input() -> None:
    with pytest.raises(InvalidFlipkartUrlError, match="URL cannot be empty"):
        validate_flipkart_url("")
    with pytest.raises(InvalidFlipkartUrlError, match="URL cannot be empty"):
        validate_flipkart_url("   ")


def test_extract_title_hint_edge_cases() -> None:
    assert extract_title_hint_from_path("") is None
    assert extract_title_hint_from_path("/p/itm123") is None
    assert extract_title_hint_from_path("/samsung-galaxy-s24-ultra/p/itm1") == "Samsung Galaxy S24 Ultra"
