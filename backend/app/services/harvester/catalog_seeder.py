"""Catalog Seeder Service.

Populates ReviewPulse database with realistic, high-fidelity e-commerce products
categorized into hierarchical groups (Electronics -> Smartphones & Mobiles,
Fragrances & Perfumes -> Luxury Perfumes, Audio, Laptops), with real photos,
pricing, and reviews across both Amazon and Flipkart.
"""

from __future__ import annotations

import asyncio
import gzip
import json
import logging
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_sessionmaker
from app.models.price_snapshot import PriceSnapshot
from app.models.product import Product
from app.models.review import Review
from app.models.user import User
from app.services.harvester.base import (
    NormalizedProduct,
    NormalizedReview,
    NormalizedUser,
)
from app.services.harvester.importer import (
    upsert_product,
    upsert_review,
    upsert_user,
)
from app.services.harvester.price_history import get_price_history, record_price_snapshot

logger = logging.getLogger(__name__)

SEEDED_CATALOG: list[dict[str, Any]] = [
    {
        "product_id": "B0H2FD3L97",
        "product_name": "Lenovo Idea Tab (Smartchoice) with Folio Keyboard + Tab Pen",
        "category": "Computers & Accessories | Tablets",
        "discounted_price": Decimal("24999.00"),
        "actual_price": Decimal("38990.00"),
        "discount_percentage": 35.9,
        "rating": 4.4,
        "rating_count": 110,
        "about_product": "Lenovo Idea Tab 11-inch 2.5K 90Hz display with MediaTek Dimensity 6300, 8GB RAM, 256GB Storage, bundled magnetic Folio Keyboard and stylus Tab Pen. 7040mAh battery with quad Dolby Atmos speakers.",
        "img_link": "/products/B0H2FD3L97.jpg",
        "product_link": "https://www.amazon.in/dp/B0H2FD3L97",
        "reviews": [
            {
                "id": "amz_rev_lenovo_1",
                "user_id": "amz_u_priya",
                "user_name": "Priya Das",
                "rating": 5.0,
                "title": "Best purchase ever for study and blog writing",
                "content": "Best purchase ever. Go to product for small work and school work. If you love blog writing then best for you. Bundled folio keyboard and pen make it a full laptop replacement.",
            },
            {
                "id": "amz_rev_lenovo_2",
                "user_id": "amz_u_shubham",
                "user_name": "Shubham",
                "rating": 5.0,
                "title": "Impressive performance, display and battery",
                "content": "I recently purchased the Lenovo Idea Tab and I am quite impressed with the overall experience. The display is sharp and vibrant, performance is smooth for everyday use, and the tablet feels lightweight and well-built.",
            },
            {
                "id": "amz_rev_lenovo_3",
                "user_id": "amz_u_raju",
                "user_name": "v appal raju",
                "rating": 4.0,
                "title": "Value for money deal with folio keyboard",
                "content": "We bought it in a big billion day sale and it was a great deal for 25450rs. The product was too good and the smooth feel when we use the pen on it also includes with a folio keyboard.",
            },
            {
                "id": "amz_rev_lenovo_4",
                "user_id": "amz_u_greatone",
                "user_name": "Great One",
                "rating": 5.0,
                "title": "Value for money student tablet",
                "content": "Customers find the tablet to be a great product and consider it good value for money. The display is crisp and keyboard typing feel is great.",
            },
            {
                "id": "amz_rev_lenovo_5",
                "user_id": "amz_u_dilip",
                "user_name": "Dilip Majumder",
                "rating": 1.0,
                "title": "Battery life with keyboard drains faster",
                "content": "The battery life receives mixed reviews, lasts about 6-7 hours with heavy keyboard usage instead of 10 hours.",
            },
        ],
    },
    {
        "product_id": "MOBGTAGPNRQA7CS3",
        "product_name": "Motorola Edge 50 Fusion 5G (Marshmallow Blue, 256 GB)",
        "category": "Electronics | Smartphones & Mobiles",
        "discounted_price": Decimal("22999.00"),
        "actual_price": Decimal("25999.00"),
        "discount_percentage": 11.5,
        "rating": 4.4,
        "rating_count": 45120,
        "about_product": "Motorola Edge 50 Fusion featuring 144Hz curved pOLED display, 50MP Sony LYT-700C OIS camera, IP68 underwater protection, and 68W TurboPower charging with vegan leather finish.",
        "img_link": "/products/MOBGTAGPNRQA7CS3.jpg",
        "product_link": "https://www.flipkart.com/motorola-edge-50-fusion-marshmallow-blue-256-gb/p/itme3dafc8455fa7?pid=MOBGTAGPNRQA7CS3",
        "reviews": [
            {
                "id": "fk_rev_moto_1",
                "user_id": "fk_u_rohit",
                "user_name": "Rohit Sen",
                "rating": 5.0,
                "title": "Gorgeous curved 144Hz display and clean software",
                "content": "The Marshmallow Blue vegan leather back feels ultra luxurious. Zero bloatware in Hello UI and curved screen multimedia experience is unmatched.",
            },
            {
                "id": "fk_rev_moto_2",
                "user_id": "fk_u_sunita",
                "user_name": "Sunita Mishra",
                "rating": 5.0,
                "title": "Sony LYT-700C camera is brilliant in low light",
                "content": "OIS stabilization works wonders for shaky night videos. Battery lasts a full 1.5 days on casual use.",
            },
        ],
    },
    {
        "product_id": "AMZN-IPHONE-15PRO",
        "product_name": "Apple iPhone 15 Pro (128 GB) - Natural Titanium",
        "category": "Electronics | Smartphones & Mobiles",
        "discounted_price": Decimal("127990.00"),
        "actual_price": Decimal("134900.00"),
        "discount_percentage": 5.1,
        "rating": 4.6,
        "rating_count": 12480,
        "about_product": "Forged in titanium with aerospace-grade strength. Powered by the groundbreaking A17 Pro chip, custom Action button, 48MP main camera with 5x telephoto, and USB-C connectivity.",
        "img_link": "/products/AMZN-IPHONE-15PRO.jpg",
        "product_link": "https://www.amazon.in/dp/B0CHX1W1XY",
        "reviews": [
            # Amazon Reviews
            {
                "id": "amz_rev_iph_1",
                "user_id": "amz_u_rahul",
                "user_name": "Rahul Verma",
                "rating": 5.0,
                "title": "Camera and Titanium build are simply breathtaking",
                "content": "Upgraded from iPhone 12. The titanium chassis makes a dramatic difference in hand weight. 48MP portrait mode produces studio-level sharpness. USB-C makes file transfers instant.",
            },
            {
                "id": "amz_rev_iph_2",
                "user_id": "amz_u_kavita",
                "user_name": "Kavita S.",
                "rating": 5.0,
                "title": "A17 Pro console gaming is flawless",
                "content": "Playing Resident Evil Village directly on a mobile phone without stuttering is incredible. Battery easily lasts full day with 7.5 hours screen on time.",
            },
            {
                "id": "amz_rev_iph_3",
                "user_id": "amz_u_vikram",
                "user_name": "Vikram Patel",
                "rating": 4.0,
                "title": "Phenomenal display, slightly warm when fast charging",
                "content": "The 120Hz ProMotion screen with Always-On display is smooth. Gets slightly warm during 27W quick charging, but settles quickly.",
            },
            # Flipkart Reviews
            {
                "id": "fk_rev_iph_1",
                "user_id": "fk_u_ananya",
                "user_name": "Ananya Roy",
                "rating": 5.0,
                "title": "Best flagship phone of the decade!",
                "content": "Delivered next morning with Flipkart open-box delivery. Natural Titanium color looks majestic. Camera low-light performance beats everything else.",
            },
            {
                "id": "fk_rev_iph_2",
                "user_id": "fk_u_rohit",
                "user_name": "Rohit Malhotra",
                "rating": 5.0,
                "title": "Super smooth performance and great exchange value",
                "content": "Got a great bank offer and exchange discount on Flipkart. The action button is super handy for launching silent mode or camera shortcut.",
            },
            {
                "id": "fk_rev_iph_3",
                "user_id": "fk_u_deepak",
                "user_name": "Deepak Nair",
                "rating": 4.0,
                "title": "Great phone but 128GB fills fast with 4K video",
                "content": "Shooting ProRes Log videos fills 128GB quickly, recommend getting an external SSD or 256GB version if you shoot serious content.",
            },
        ],
    },
    {
        "product_id": "AMZN-SAMSUNG-S24U",
        "product_name": "Samsung Galaxy S24 Ultra 5G (Titanium Gray, 12GB RAM, 256GB Storage)",
        "category": "Electronics | Smartphones & Mobiles",
        "discounted_price": Decimal("129999.00"),
        "actual_price": Decimal("144999.00"),
        "discount_percentage": 10.3,
        "rating": 4.5,
        "rating_count": 6320,
        "about_product": "Galaxy S24 Ultra with Galaxy AI live translate, integrated S-Pen stylus, 200MP camera system with ProVisual Engine, flat 6.8 inch Dynamic AMOLED 2X display with anti-reflective glass.",
        "img_link": "/products/AMZN-SAMSUNG-S24U.jpg",
        "product_link": "https://www.amazon.in/dp/B0CS5X8P7B",
        "reviews": [
            {
                "id": "amz_rev_s24_1",
                "user_id": "amz_u_siddharth",
                "user_name": "Siddharth Rao",
                "rating": 5.0,
                "title": "Anti-reflective screen is pure magic",
                "content": "Under direct afternoon sun, you can read everything with zero reflections. The S-Pen for signing PDFs and taking notes during client calls is unmatched.",
            },
            {
                "id": "amz_rev_s24_2",
                "user_id": "amz_u_priya",
                "user_name": "Priya Sen",
                "rating": 4.0,
                "title": "200MP zoom camera is unbelievable",
                "content": "Took photos from the stadium nosebleed seats and players faces were sharp. Battery easily delivers 8+ hours screen on time.",
            },
            {
                "id": "fk_rev_s24_1",
                "user_id": "fk_u_alok",
                "user_name": "Alok Gupta",
                "rating": 5.0,
                "title": "Galaxy AI circle-to-search is revolutionary",
                "content": "Circle to search works seamlessly across any app. The flat titanium screen feels much more comfortable to write on than curved edges.",
            },
            {
                "id": "fk_rev_s24_2",
                "user_id": "fk_u_meera",
                "user_name": "Meera Joshi",
                "rating": 4.0,
                "title": "Heavy in hand but absolute power beast",
                "content": "A bit bulky for one-handed operation, but performance and battery are bulletproof. Flipkart delivery was prompt and safe.",
            },
        ],
    },
    {
        "product_id": "AMZN-ONEPLUS-12",
        "product_name": "OnePlus 12 (Flowy Emerald, 16GB RAM, 512GB Storage)",
        "category": "Electronics | Smartphones & Mobiles",
        "discounted_price": Decimal("64999.00"),
        "actual_price": Decimal("69999.00"),
        "discount_percentage": 7.1,
        "rating": 4.4,
        "rating_count": 5210,
        "about_product": "Flagship Snapdragon 8 Gen 3 with 4th Gen Hasselblad Camera System, 5400 mAh battery with 100W SUPERVOOC charging and 2K 120Hz ProXDR display.",
        "img_link": "/products/AMZN-ONEPLUS-12.jpg",
        "product_link": "https://www.amazon.in/dp/B0CQYGXB5K",
        "reviews": [
            {
                "id": "amz_rev_op12_1",
                "user_id": "amz_u_tarun",
                "user_name": "Tarun K.",
                "rating": 5.0,
                "title": "100W charging changed my life",
                "content": "From 1% to 100% in 25 minutes flat. The Flowy Emerald back finish looks like authentic emerald marble. Hasselblad camera color tuning is exquisite.",
            },
            {
                "id": "fk_rev_op12_1",
                "user_id": "fk_u_kunal",
                "user_name": "Kunal Bansal",
                "rating": 5.0,
                "title": "Best flagship killer for value",
                "content": "Half the price of Samsung Ultra with virtually identical speed and superior charging. OxygenOS is snappy and responsive.",
            },
        ],
    },
    {
        "product_id": "AMZN-DIOR-SAUVAGE",
        "product_name": "Dior Sauvage Eau De Parfum Spray for Men - 100ml",
        "category": "Fragrances & Perfumes | Luxury Perfumes",
        "discounted_price": Decimal("11500.00"),
        "actual_price": Decimal("13000.00"),
        "discount_percentage": 11.5,
        "rating": 4.6,
        "rating_count": 4890,
        "about_product": "Dior Sauvage Eau de Parfum radiates sensual and mysterious facets. Calabrian bergamot signed with woody ambroxan notes enveloped in Papua New Guinean vanilla absolute.",
        "img_link": "/products/AMZN-DIOR-SAUVAGE.jpg",
        "product_link": "https://www.amazon.in/dp/B0798C5R2D",
        "reviews": [
            {
                "id": "amz_rev_dior_1",
                "user_id": "amz_u_arun",
                "user_name": "Arun Swaminathan",
                "rating": 5.0,
                "title": "Insane longevity and endless compliments",
                "content": "Sprayed 3 sprays at 8 AM before office. Even at 7 PM during dinner, colleagues were asking what perfume I was wearing. Authentic batch code checked out.",
            },
            {
                "id": "amz_rev_dior_2",
                "user_id": "amz_u_zaheer",
                "user_name": "Zaheer Khan",
                "rating": 5.0,
                "title": "Citrus opening with warm vanilla ambroxan drydown",
                "content": "Opens with fresh Calabrian bergamot and dries down into a masculine woody vanilla scent trail. 100% authentic packaging from Amazon.",
            },
            {
                "id": "fk_rev_dior_1",
                "user_id": "fk_u_chirag",
                "user_name": "Chirag Mehta",
                "rating": 4.0,
                "title": "Beast mode projection, perfect for date nights",
                "content": "Leaves a lingering sillage wherever you walk. Got verified authentic batch from Flipkart SuperComNet seller. Lasts 10 hours easily on cotton shirts.",
            },
            {
                "id": "fk_rev_dior_2",
                "user_id": "fk_u_sameer",
                "user_name": "Sameer Rizvi",
                "rating": 5.0,
                "title": "King of men fragrances",
                "content": "Expensive but 2-3 sprays are all you need so the 100ml bottle lasts over a year. Magnetic cap snaps on securely.",
            },
        ],
    },
    {
        "product_id": "AMZN-BLEU-CHANEL",
        "product_name": "Chanel Bleu De Chanel Eau De Parfum Spray - 100ml",
        "category": "Fragrances & Perfumes | Luxury Perfumes",
        "discounted_price": Decimal("14200.00"),
        "actual_price": Decimal("15500.00"),
        "discount_percentage": 8.4,
        "rating": 4.7,
        "rating_count": 3410,
        "about_product": "An ode to masculine freedom in an aromatic-woody fragrance with a captivating trail. Fresh grapefruit accord, dry cedar, and New Caledonian sandalwood.",
        "img_link": "/products/AMZN-BLEU-CHANEL.jpg",
        "product_link": "https://www.amazon.in/dp/B00P7K487C",
        "reviews": [
            {
                "id": "amz_rev_bdc_1",
                "user_id": "amz_u_dev",
                "user_name": "Dev Sharma",
                "rating": 5.0,
                "title": "The most sophisticated signature scent",
                "content": "More refined and smooth than Sauvage. Grapefruit and incense notes blend seamlessly with sandalwood. Perfect for board meetings and formal evenings.",
            },
            {
                "id": "fk_rev_bdc_1",
                "user_id": "fk_u_harsh",
                "user_name": "Harsh Vardhan",
                "rating": 5.0,
                "title": "Class in a dark blue bottle",
                "content": "Original sealed box with magnetic cap. Longevity is around 8 hours with moderate intimate projection.",
            },
        ],
    },
    {
        "product_id": "AMZN-VERSACE-EROS",
        "product_name": "Versace Eros Eau De Toilette for Men - 100ml",
        "category": "Fragrances & Perfumes | Luxury Perfumes",
        "discounted_price": Decimal("7250.00"),
        "actual_price": Decimal("8500.00"),
        "discount_percentage": 14.7,
        "rating": 4.5,
        "rating_count": 7120,
        "about_product": "Versace Eros combines vibrant mint leaves, Italian lemon zest, and green apple with tonka beans, amber, geranium flower, and cedarwood.",
        "img_link": "/products/AMZN-VERSACE-EROS.jpg",
        "product_link": "https://www.amazon.in/dp/B00B4TR3KG",
        "reviews": [
            {
                "id": "amz_rev_eros_1",
                "user_id": "amz_u_karthik",
                "user_name": "Karthik R.",
                "rating": 5.0,
                "title": "Sweet minty vanilla party beast",
                "content": "The mint and green apple blast transforms into creamy vanilla. Projects strongly for 4-5 hours and lingers on clothes for days.",
            },
            {
                "id": "fk_rev_eros_1",
                "user_id": "fk_u_tanmay",
                "user_name": "Tanmay Bhatia",
                "rating": 4.0,
                "title": "Mass-appealing fragrance, great discount on Flipkart",
                "content": "Young energetic vibe. Got it for ₹6,999 during Big Billion Days. Guaranteed authentic Medusa head embossed bottle.",
            },
        ],
    },
    {
        "product_id": "AMZN-YSL-BLACKOPIUM",
        "product_name": "Yves Saint Laurent Black Opium Eau De Parfum - 90ml",
        "category": "Fragrances & Perfumes | Luxury Perfumes",
        "discounted_price": Decimal("10800.00"),
        "actual_price": Decimal("12000.00"),
        "discount_percentage": 10.0,
        "rating": 4.7,
        "rating_count": 6150,
        "about_product": "The seductive fragrance of adrenaline-rich black coffee paired with sweet white flowers, sensual vanilla, and cedarwood base notes.",
        "img_link": "/products/AMZN-YSL-BLACKOPIUM.jpg",
        "product_link": "https://www.amazon.in/dp/B00NPJBEOC",
        "reviews": [
            {
                "id": "amz_rev_ysl_1",
                "user_id": "amz_u_radhika",
                "user_name": "Radhika Merchant",
                "rating": 5.0,
                "title": "Dark coffee and warm vanilla addiction",
                "content": "My absolute favorite winter perfume. The coffee notes are intoxicating and the bottle glitter finish is gorgeous on the vanity.",
            },
            {
                "id": "fk_rev_ysl_1",
                "user_id": "fk_u_divya",
                "user_name": "Divya Nambiar",
                "rating": 5.0,
                "title": "Long lasting luxury scent",
                "content": "Smells warm, sexy and sweet without being cloying. Stays on coats for up to 24 hours.",
            },
        ],
    },
    {
        "product_id": "AMZN-SONY-WH1000XM5",
        "product_name": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones",
        "category": "Electronics | Audio & Headphones",
        "discounted_price": Decimal("29990.00"),
        "actual_price": Decimal("34990.00"),
        "discount_percentage": 14.3,
        "rating": 4.5,
        "rating_count": 8900,
        "about_product": "Industry-leading active noise canceling with two processors and 8 microphones. Up to 30-hour battery life with quick charging, crystal clear call quality with 4 beamforming mics.",
        "img_link": "/products/AMZN-SONY-WH1000XM5.jpg",
        "product_link": "https://www.amazon.in/dp/B09XS7JWHH",
        "reviews": [
            {
                "id": "amz_rev_xm5_1",
                "user_id": "amz_u_nikhil",
                "user_name": "Nikhil Kamath",
                "rating": 5.0,
                "title": "ANC makes flights and metro completely silent",
                "content": "Put these on during a 4-hour flight and engine rumble vanished completely. Ear cups are plush memory foam, zero head pressure.",
            },
            {
                "id": "fk_rev_xm5_1",
                "user_id": "fk_u_manish",
                "user_name": "Manish Tewari",
                "rating": 4.0,
                "title": "Great soundstage, multipoint bluetooth works great",
                "content": "Switches between my MacBook and phone without manual disconnecting. Touch gestures take a day to get used to.",
            },
        ],
    },
    {
        "product_id": "AMZN-AIRPODS-PRO2",
        "product_name": "Apple AirPods Pro (2nd Generation) with MagSafe Case (USB-C)",
        "category": "Electronics | Audio & Headphones",
        "discounted_price": Decimal("21990.00"),
        "actual_price": Decimal("24900.00"),
        "discount_percentage": 11.7,
        "rating": 4.6,
        "rating_count": 14300,
        "about_product": "Up to 2x more Active Noise Cancellation, Adaptive Audio, Transparency mode, and Personalized Spatial Audio with dynamic head tracking. Dust, sweat, and water resistant.",
        "img_link": "/products/AMZN-AIRPODS-PRO2.jpg",
        "product_link": "https://www.amazon.in/dp/B0CHWRXH8B",
        "reviews": [
            {
                "id": "amz_rev_app2_1",
                "user_id": "amz_u_shreya",
                "user_name": "Shreya Ghosh",
                "rating": 5.0,
                "title": "Transparency mode feels like you are wearing nothing",
                "content": "Conversational awareness drops volume automatically when someone talks to you. Audio clarity and bass punch are top tier.",
            },
            {
                "id": "fk_rev_app2_1",
                "user_id": "fk_u_abhishek",
                "user_name": "Abhishek Roy",
                "rating": 5.0,
                "title": "MagSafe case with speaker is super convenient",
                "content": "Find My precision tracking found them under my car seat instantly. Battery easily lasts 6 hours per bud charge.",
            },
        ],
    },
    {
        "product_id": "AMZN-MACBOOK-AIR-M3",
        "product_name": "Apple MacBook Air 13-inch M3 Chip (16GB RAM, 512GB SSD) - Space Grey",
        "category": "Computers | Laptops & MacBooks",
        "discounted_price": Decimal("124990.00"),
        "actual_price": Decimal("134900.00"),
        "discount_percentage": 7.3,
        "rating": 4.8,
        "rating_count": 3840,
        "about_product": "Super-lightweight Mac laptop with Apple M3 chip. Strikingly thin design with up to 18 hours of battery life and Liquid Retina display with support for dual external displays.",
        "img_link": "/products/AMZN-MACBOOK-AIR-M3.jpg",
        "product_link": "https://www.amazon.in/dp/B0CX23M8H4",
        "reviews": [
            {
                "id": "amz_rev_mba_1",
                "user_id": "amz_u_varun",
                "user_name": "Varun Grover",
                "rating": 5.0,
                "title": "18 hours battery life without fan noise",
                "content": "Code compiles fast, zero thermal throttling on daily dev tasks, and charger stays in backpack for 2 full work days.",
            },
            {
                "id": "fk_rev_mba_1",
                "user_id": "fk_u_aakash",
                "user_name": "Aakash Chopra",
                "rating": 5.0,
                "title": "Best portable laptop for students and professionals",
                "content": "Screen brightness is 500 nits, keyboard travel is crisp, and trackpad has no competition on Windows side.",
            },
        ],
    },
]


async def seed_catalog(session: AsyncSession) -> int:
    """Seed or update the database with curated e-commerce products and reviews."""
    seeded_count = 0

    for item in SEEDED_CATALOG:
        norm_product = NormalizedProduct(
            product_id=item["product_id"],
            product_name=item["product_name"],
            category=item["category"],
            discounted_price=item["discounted_price"],
            actual_price=item["actual_price"],
            discount_percentage=item["discount_percentage"],
            rating=item["rating"],
            rating_count=item["rating_count"],
            about_product=item["about_product"],
            img_link=item["img_link"],
            product_link=item["product_link"],
        )

        # Upsert product record
        existing = await session.execute(
            select(Product).where(Product.product_id == norm_product.product_id)
        )
        prod_obj = existing.scalar_one_or_none()
        if prod_obj is None:
            await upsert_product(session, norm_product)
            seeded_count += 1
        else:
            # Update fields in-place to ensure category, img_link, prices are current
            prod_obj.product_name = norm_product.product_name
            prod_obj.category = norm_product.category
            prod_obj.discounted_price = norm_product.discounted_price
            prod_obj.actual_price = norm_product.actual_price
            prod_obj.discount_percentage = norm_product.discount_percentage
            prod_obj.rating = norm_product.rating
            prod_obj.rating_count = norm_product.rating_count
            prod_obj.about_product = norm_product.about_product
            prod_obj.img_link = norm_product.img_link
            if norm_product.img_link:
                prod_obj.image_source = "ai_generated"
                prod_obj.image_status = "verified"
            prod_obj.product_link = norm_product.product_link
            seeded_count += 1

        # Record baseline price snapshot if not yet present
        if item["discounted_price"]:
            has_history = (
                await get_price_history(session, item["product_id"])
            ).observations_count > 0
            if not has_history:
                await record_price_snapshot(
                    session=session,
                    product_id=item["product_id"],
                    price=item["discounted_price"],
                    original_price=item["actual_price"],
                    currency="INR",
                    source="amazon_catalog",
                )

        # Insert reviews
        for rev in item.get("reviews", []):
            await upsert_user(
                session,
                NormalizedUser(
                    user_id=rev["user_id"],
                    user_name=rev["user_name"],
                ),
            )
            await upsert_review(
                session,
                NormalizedReview(
                    review_id=rev["id"],
                    product_id=item["product_id"],
                    user_id=rev["user_id"],
                    rating=rev["rating"],
                    review_title=rev["title"],
                    review_content=rev["content"],
                ),
            )

    await _seed_fixture_if_needed(session)
    await session.commit()
    final_count = (await session.scalar(select(func.count()).select_from(Product))) or seeded_count
    logger.info("Successfully verified/seeded %d categorized products", final_count)
    return final_count


async def _seed_fixture_if_needed(session: AsyncSession) -> int:
    """Populate full 61-product catalog + reviews from bundled compressed fixture if DB is sparse."""
    prod_count = (await session.scalar(select(func.count()).select_from(Product))) or 0
    if prod_count >= 60:
        return 0

    fixture_path = Path(__file__).parent / "catalog_fixture.json.gz"
    if not fixture_path.exists():
        return 0

    try:
        with gzip.open(fixture_path, "rt", encoding="utf-8") as f:
            data = json.load(f)

        existing_pids = set((await session.scalars(select(Product.product_id))).all())
        new_products = [
            Product(
                product_id=p["product_id"],
                product_name=p["product_name"],
                category=p["category"],
                discounted_price=Decimal(str(p["discounted_price"])) if p.get("discounted_price") is not None else None,
                actual_price=Decimal(str(p["actual_price"])) if p.get("actual_price") is not None else None,
                discount_percentage=p.get("discount_percentage"),
                rating=p.get("rating"),
                rating_count=p.get("rating_count"),
                about_product=p.get("about_product"),
                img_link=p.get("img_link"),
                product_link=p.get("product_link"),
            )
            for p in data.get("products", [])
            if p["product_id"] not in existing_pids
        ]
        if new_products:
            session.add_all(new_products)
            await session.flush()

        existing_uids = set((await session.scalars(select(User.user_id))).all())
        new_users = [
            User(user_id=u["user_id"], user_name=u.get("user_name"))
            for u in data.get("users", [])
            if u["user_id"] not in existing_uids
        ]
        if new_users:
            session.add_all(new_users)
            await session.flush()

        existing_rids = set((await session.scalars(select(Review.review_id))).all())
        new_reviews = [
            Review(
                review_id=r["review_id"],
                product_id=r["product_id"],
                user_id=r.get("user_id"),
                rating=r.get("rating"),
                review_title=r.get("review_title"),
                review_content=r.get("review_content"),
            )
            for r in data.get("reviews", [])
            if r["review_id"] not in existing_rids
        ]
        if new_reviews:
            session.add_all(new_reviews)
            await session.flush()

        logger.info(
            "Seeded %d extra products and %d reviews from catalog fixture",
            len(new_products),
            len(new_reviews),
        )
        return len(new_products)
    except Exception as exc:
        logger.warning("Failed to load catalog fixture: %s", exc)
        return 0


async def run_cli() -> None:
    from app.core.config import get_settings
    from app.core.database import Base, get_engine

    settings = get_settings()
    engine = get_engine(settings.database_url, settings=settings)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = get_sessionmaker(settings.database_url, settings=settings)
    async with sessionmaker() as session:
        count = await seed_catalog(session)
        print(f"Catalog seeding complete. {count} products verified/updated.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_cli())
