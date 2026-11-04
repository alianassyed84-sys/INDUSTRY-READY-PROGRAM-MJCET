"""Quick standalone test script for Telegram mobile price alert notifications.

Usage:
    python automations/n8n/test_telegram_alert.py <BOT_TOKEN> <CHAT_ID>

Example:
    python automations/n8n/test_telegram_alert.py 123456789:ABCdefGHI 987654321
"""

from __future__ import annotations

import sys
import urllib.parse
import urllib.request
import json
from datetime import datetime


def send_test_alert(bot_token: str, chat_id: str, alert_type: str = "drop") -> bool:
    if alert_type == "drop":
        message = (
            "🟢 <b>PRICE DROP ALERT!</b> 🔥 <i>ALL-TIME LOW!</i>\n\n"
            "📦 <b>Apple iPhone 15 (128 GB) - Black</b>\n"
            "💰 <b>New Price:</b> <code>₹54,999</code>\n"
            "<s>Original Price: ₹79,900</s>\n"
            "🎉 <b>You Save:</b> ₹24,901 (-31.2%)\n\n"
            "🆔 <b>Product ID:</b> <code>B0CHX1W1XY</code>\n"
            f"⏰ <b>Updated:</b> {datetime.now().strftime('%I:%M %p')}\n"
            "⚡ <i>Automated by ReviewPulse Neural Engine</i>"
        )
    else:
        message = (
            "🔴 <b>PRICE INCREASE NOTICE!</b>\n\n"
            "📦 <b>Sony WH-1000XM5 Wireless Headphones</b>\n"
            "💰 <b>New Price:</b> <code>₹29,990</code>\n"
            "<s>Previous Price: ₹26,990</s>\n"
            "📈 <b>Increased By:</b> +₹3,000 (+11.1%)\n\n"
            "🆔 <b>Product ID:</b> <code>B09XS7JWHH</code>\n"
            f"⏰ <b>Updated:</b> {datetime.now().strftime('%I:%M %p')}\n"
            "⚡ <i>Automated by ReviewPulse Neural Engine</i>"
        )

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
            status = resp.status
            body = json.loads(resp.read().decode("utf-8"))
            if status == 200 and body.get("ok"):
                print(f"[{alert_type.upper()}] Success! Push notification sent to your phone.")
                return True
            print(f"[{alert_type.upper()}] Failed with response: {body}")
            return False
    except urllib.error.HTTPError as exc:
        err_msg = exc.read().decode("utf-8")
        print(f"[{alert_type.upper()}] HTTP Error {exc.code}: {err_msg}")
        return False
    except Exception as exc:
        print(f"[{alert_type.upper()}] Connection Error: {exc}")
        return False


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python automations/n8n/test_telegram_alert.py <BOT_TOKEN> <CHAT_ID>")
        print("\nExample:")
        print("    python automations/n8n/test_telegram_alert.py 123456789:ABCdefGHI 987654321")
        sys.exit(1)

    bot_token = sys.argv[1].strip()
    chat_id = sys.argv[2].strip()

    print(f"Sending sample price drop alert to Telegram chat ID: {chat_id}...")
    success_drop = send_test_alert(bot_token, chat_id, alert_type="drop")

    print("\nSending sample price increase notice...")
    success_hike = send_test_alert(bot_token, chat_id, alert_type="hike")

    if success_drop and success_hike:
        print("\n[ALL TESTS PASSED] Telegram integration verified! Your phone received both alerts.")
    else:
        print("\n[!] Please verify your BOT_TOKEN and CHAT_ID.")


if __name__ == "__main__":
    main()
