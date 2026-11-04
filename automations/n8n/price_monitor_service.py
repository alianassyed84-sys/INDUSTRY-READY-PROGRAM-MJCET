"""ReviewPulse Continuous Price Monitor Service.

Monitors live products on ReviewPulse Vercel/Onrender API (or local backend)
and sends instant mobile push notifications to Telegram when prices drop or increase.
Also accepts live Amazon and Flipkart product URLs to add them to tracking.

Usage:
    python automations/n8n/price_monitor_service.py --once
    python automations/n8n/price_monitor_service.py --daemon
    python automations/n8n/price_monitor_service.py --trigger-live
    python automations/n8n/price_monitor_service.py --add-url "https://www.flipkart.com/..."
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("ReviewPulsePriceMonitor")

DEFAULT_API_URL = os.environ.get("API_URL", "https://irpversion2-2.onrender.com")
DEFAULT_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9149329197:AAEMiSz8nhY0Oc-BCPVgo5xJfN2kMHPTFSw")
DEFAULT_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7154556693")
DEFAULT_AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "dev-token")
MIN_PRICE_DELTA = float(os.environ.get("MIN_PRICE_DELTA", 50.0))

CACHE_FILE = Path(__file__).parent / "price_cache.json"


def load_cache() -> dict[str, float]:
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_cache(cache: dict[str, float]) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as exc:
        logger.warning(f"Failed to persist price cache: {exc}")


def fetch_products(api_url: str, auth_token: str) -> list[dict]:
    endpoint = f"{api_url.rstrip('/')}/api/v1/harvester/products?limit=50"
    req = urllib.request.Request(
        endpoint,
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Accept": "application/json",
            "User-Agent": "ReviewPulse-Monitor/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("items", [])
    except Exception as exc:
        logger.error(f"Failed to fetch products from {endpoint}: {exc}")
        return []


def add_url_for_tracking(
    url: str,
    api_url: str = DEFAULT_API_URL,
    auth_token: str = DEFAULT_AUTH_TOKEN,
) -> dict | None:
    """Analyze an incoming Amazon or Flipkart URL and record it in ReviewPulse database."""
    endpoint = f"{api_url.rstrip('/')}/api/v1/harvester/analyze-url"
    payload = {"url": url.strip()}
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json",
            "User-Agent": "ReviewPulse-Monitor/1.0",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("product")
    except Exception as exc:
        logger.error(f"Failed to add URL {url}: {exc}")
        return None


def send_telegram_alert(bot_token: str, chat_id: str, message: str) -> bool:
    endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    req = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return bool(resp.status == 200 and body.get("ok"))
    except Exception as exc:
        logger.error(f"Failed to send Telegram alert: {exc}")
        return False


def format_inr(val: float) -> str:
    try:
        s = f"{int(round(val))}"
        if len(s) <= 3:
            return f"₹{s}"
        last_three = s[-3:]
        remaining = s[:-3]
        groups = []
        while remaining:
            groups.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        return f"₹{','.join(groups)},{last_three}"
    except Exception:
        return f"₹{val:,.0f}"


def format_alert_message(
    product_name: str,
    product_id: str,
    current_price: float,
    previous_price: float,
    is_drop: bool,
    source: str = "Vercel Live Production",
) -> str:
    delta = abs(current_price - previous_price)
    pct = (delta / previous_price * 100) if previous_price > 0 else 0.0

    curr_str = format_inr(current_price)
    prev_str = format_inr(previous_price)
    delta_str = format_inr(delta)
    pct_str = f"{pct:.1f}%"

    if is_drop:
        header = "🟢 <b>LIVE: PRICE DROP ALERT!</b> 🔥"
        diff_line = f"🎉 <b>You Save:</b> {delta_str} (-{pct_str})"
    else:
        header = "🔴 <b>LIVE: PRICE INCREASE NOTICE!</b>"
        diff_line = f"📈 <b>Increased By:</b> +{delta_str} (+{pct_str})"

    return (
        f"{header}\n\n"
        f"📦 <b>{product_name}</b>\n"
        f"💰 <b>Current Price:</b> <code>{curr_str}</code>\n"
        f"<s>Previous Price: {prev_str}</s>\n"
        f"{diff_line}\n\n"
        f"🆔 <b>ID:</b> <code>{product_id}</code>\n"
        f"🌐 <b>Source:</b> {source}\n"
        f"⏰ <b>Checked:</b> {datetime.now().strftime('%I:%M %p')}\n"
        f"⚡ <i>ReviewPulse Neural Engine Automation</i>"
    )


def check_and_alert(
    api_url: str = DEFAULT_API_URL,
    bot_token: str = DEFAULT_BOT_TOKEN,
    chat_id: str = DEFAULT_CHAT_ID,
    auth_token: str = DEFAULT_AUTH_TOKEN,
    force_alert_first: bool = False,
) -> int:
    logger.info(f"Checking live products from {api_url}...")
    products = fetch_products(api_url, auth_token)
    if not products:
        logger.warning("No products returned or API is still sleeping. Will retry.")
        return 0

    cache = load_cache()
    alerts_sent = 0

    for idx, prod in enumerate(products):
        pid = prod.get("product_id") or f"prod-{idx}"
        name = prod.get("product_name") or "ReviewPulse Product"
        curr_price = prod.get("discounted_price") or prod.get("actual_price")
        if curr_price is None:
            continue
        curr_price = float(curr_price)

        prev_price = cache.get(pid)

        # If testing or force alert for the first product
        if force_alert_first and idx == 0:
            simulated_prev = curr_price + 350.0  # simulate a price drop of 350
            msg = format_alert_message(
                product_name=name,
                product_id=pid,
                current_price=curr_price,
                previous_price=simulated_prev,
                is_drop=True,
                source="https://reviewpulse-peach.vercel.app",
            )
            logger.info(f"Sending live Vercel alert for {name} ({pid})...")
            if send_telegram_alert(bot_token, chat_id, msg):
                alerts_sent += 1
            cache[pid] = curr_price
            continue

        if prev_price is not None:
            delta = curr_price - prev_price
            if abs(delta) >= MIN_PRICE_DELTA:
                is_drop = delta < 0
                msg = format_alert_message(
                    product_name=name,
                    product_id=pid,
                    current_price=curr_price,
                    previous_price=prev_price,
                    is_drop=is_drop,
                    source="https://reviewpulse-peach.vercel.app",
                )
                logger.info(f"Price change detected for {pid}: {prev_price} -> {curr_price}. Alerting...")
                if send_telegram_alert(bot_token, chat_id, msg):
                    alerts_sent += 1

        cache[pid] = curr_price

    save_cache(cache)
    logger.info(f"Finished check. Monitored {len(products)} products. Alerts sent: {alerts_sent}")
    return alerts_sent


def check_telegram_incoming_urls(
    bot_token: str = DEFAULT_BOT_TOKEN,
    chat_id: str = DEFAULT_CHAT_ID,
    api_url: str = DEFAULT_API_URL,
    auth_token: str = DEFAULT_AUTH_TOKEN,
    offset: int = 0,
) -> int:
    """Listen for URLs sent directly to the Telegram bot."""
    endpoint = f"https://api.telegram.org/bot{bot_token}/getUpdates?offset={offset}&timeout=2"
    try:
        req = urllib.request.urlopen(endpoint, timeout=5)
        data = json.loads(req.read().decode("utf-8"))
        updates = data.get("result", [])
        for u in updates:
            offset = max(offset, u.get("update_id", 0) + 1)
            msg = u.get("message", {})
            text = msg.get("text", "").strip()
            sender_id = str(msg.get("chat", {}).get("id", "")) or chat_id

            if not text:
                continue

            match = re.search(r"https?://[^\s]+", text)
            if match and ("amazon." in text.lower() or "flipkart." in text.lower()):
                product_url = match.group(0)
                logger.info(f"Received tracking request via Telegram for: {product_url}")
                send_telegram_alert(
                    bot_token,
                    sender_id,
                    "🔍 <b>Detecting product details from URL...</b>\n<i>Please wait a moment...</i>",
                )
                prod = add_url_for_tracking(product_url, api_url, auth_token)
                if prod:
                    p_name = prod.get("product_name", "E-commerce Product")
                    p_price = prod.get("discounted_price") or prod.get("actual_price") or 0.0
                    p_orig = prod.get("actual_price")

                    reply = (
                        "✅ <b>Product Successfully Added to 24/7 Price Monitor!</b>\n\n"
                        f"📦 <b>{p_name}</b>\n"
                        f"💰 <b>Current Tracked Price:</b> <code>{format_inr(float(p_price))}</code>\n"
                    )
                    if p_orig and float(p_orig) != float(p_price):
                        reply += f"<s>Original Price: {format_inr(float(p_orig))}</s>\n"
                    reply += (
                        f"\n🆔 <b>ID:</b> <code>{prod.get('product_id')}</code>\n"
                        "🔔 <i>Ab jab bhi iska price kam ya zyada hoga, aapko yahan instant notification aayega!</i>"
                    )
                    send_telegram_alert(bot_token, sender_id, reply)
                    # Add to cache immediately
                    cache = load_cache()
                    cache[prod.get("product_id")] = float(p_price)
                    save_cache(cache)
                else:
                    send_telegram_alert(
                        bot_token,
                        sender_id,
                        "⚠️ <i>Product could not be added. Please verify it is a valid Amazon.in or Flipkart URL.</i>",
                    )
    except Exception as exc:
        logger.debug(f"Update poll notice: {exc}")
    return offset


def main() -> None:
    parser = argparse.ArgumentParser(description="ReviewPulse Live Price Monitor")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously in background")
    parser.add_argument("--interval", type=int, default=3600, help="Poll interval in seconds (default: 3600)")
    parser.add_argument("--trigger-live", action="store_true", help="Fetch live Vercel product and send live alert now")
    parser.add_argument("--add-url", type=str, help="Add Amazon/Flipkart URL for tracking")
    parser.add_argument("--api-url", default=DEFAULT_API_URL, help="Backend API URL")
    args = parser.parse_args()

    if args.add_url:
        print(f"[*] Adding URL for 24/7 price tracking: {args.add_url}")
        prod = add_url_for_tracking(args.add_url, api_url=args.api_url)
        if prod:
            print(f"[SUCCESS] Product added: {prod.get('product_name')} (ID: {prod.get('product_id')})")
            price = prod.get("discounted_price") or prod.get("actual_price")
            print(f"[PRICE] Current price: {format_inr(float(price or 0))}")
            # Alert user on Telegram too
            send_telegram_alert(
                DEFAULT_BOT_TOKEN,
                DEFAULT_CHAT_ID,
                f"✅ <b>Added via CLI:</b> {prod.get('product_name')} ({format_inr(float(price or 0))})"
            )
        else:
            print("[ERROR] Failed to extract product details from URL.")
        return

    if args.trigger_live:
        print("[*] Triggering live alert from Vercel production API...")
        check_and_alert(api_url=args.api_url, force_alert_first=True)
        return

    if args.once:
        check_and_alert(api_url=args.api_url)
        return

    if args.daemon:
        logger.info(f"Starting continuous daemon (interval: {args.interval}s, Telegram URL listener active)...")
        last_check = 0
        offset = 0
        while True:
            try:
                now = time.time()
                # Check Telegram bot for incoming URLs every 5 seconds
                offset = check_telegram_incoming_urls(offset=offset, api_url=args.api_url)

                # Run price check every interval
                if now - last_check >= args.interval:
                    check_and_alert(api_url=args.api_url)
                    last_check = now

            except Exception as exc:
                logger.error(f"Error during daemon cycle: {exc}")
            time.sleep(5)


if __name__ == "__main__":
    main()
