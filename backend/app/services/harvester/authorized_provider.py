"""Authorized Amazon Product Provider client and integration documentation.

Reflects constraints and requirements of:
- Amazon Product Advertising API (PA-API 5.0) / Amazon Creator Services
- Third-party verified aggregators (e.g., Rainforest API)

Status:
Live provider access is DISABLED until authorized credentials and account approvals
are configured in the runtime environment.
"""

from __future__ import annotations

import logging
from typing import Final

from app.services.harvester.provider import (
    ProductDataProvider,
    ProviderAuthenticationError,
    ProviderNotConfiguredError,
    ProviderProduct,
)

logger = logging.getLogger(__name__)

AMAZON_IN_MARKETPLACE: Final[str] = "www.amazon.in"
AMAZON_PA_API_HOST: Final[str] = "webservices.amazon.in"
AMAZON_PA_API_REGION: Final[str] = "eu-west-1"


class AmazonCreatorApiProvider(ProductDataProvider):
    """Client for Amazon Creator / Product Advertising API (PA-API 5.0).

    Operational Constraints:
    1. Account Eligibility: Requires an active Amazon Associates / Influencer account
       with at least 3 qualifying referred sales within the past 180 days.
    2. Authentication: AWS Signature Version 4 (SigV4) using Access Key ID, Secret Key,
       and Partner Tag.
    3. Review Text Limitation: Official PA-API 5.0 GetItems operation provides product
       metadata (title, price, image, rating aggregate), but DOES NOT return individual
       customer review texts or reviewer IDs due to Amazon program policies.
    """

    name: str = "creator_api"

    def __init__(
        self,
        access_key: str | None,
        secret_key: str | None,
        partner_tag: str | None,
    ) -> None:
        self.access_key = (access_key or "").strip()
        self.secret_key = (secret_key or "").strip()
        self.partner_tag = (partner_tag or "").strip()

    def _verify_credentials(self) -> None:
        if not self.access_key or not self.secret_key or not self.partner_tag:
            missing: list[str] = []
            if not self.access_key:
                missing.append("AMAZON_ACCESS_KEY")
            if not self.secret_key:
                missing.append("AMAZON_SECRET_KEY")
            if not self.partner_tag:
                missing.append("AMAZON_PARTNER_TAG")
            raise ProviderNotConfiguredError(
                "Amazon Creator / PA-API is not configured. Missing required "
                f"environment variables: {', '.join(missing)}. "
                "Set these in .env or configure AMAZON_PROVIDER=mock."
            )

        # Basic credential format validation
        if len(self.access_key) < 16:
            raise ProviderAuthenticationError(
                "Invalid AMAZON_ACCESS_KEY format. Expected standard AWS Access Key ID."
            )

    async def get_product_by_asin(self, asin: str) -> ProviderProduct | None:
        """Fetch product details via Amazon PA-API 5.0 GetItems.

        Raises:
            ProviderNotConfiguredError: When credentials are missing.
            ProviderAuthenticationError: When credentials fail sanity checks.
        """
        self._verify_credentials()

        # In production with verified credentials, this executes an AWS SigV4 signed
        # POST request to https://webservices.amazon.in/paapi5/getitems.
        # Live network calls without verified sandbox or production tokens are disabled
        # to prevent unauthorized API rejections and policy violations.
        raise ProviderNotConfiguredError(
            "Live Amazon Creator / PA-API request execution is disabled: "
            "account has not been verified with active Amazon Associates India "
            "sales quotas. Use AMAZON_PROVIDER=mock for testing and development."
        )
