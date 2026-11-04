/**
 * Lightweight fire-and-forget Telegram notifier for price tracking actions.
 * Sends push notifications EXCLUSIVELY to the team group via Telegram Bot API
 * whenever a user starts price tracking for a product on the website.
 */

const BOT_TOKEN = '9149329197:AAEMiSz8nhY0Oc-BCPVgo5xJfN2kMHPTFSw';
// Strictly send to Team Supergroup only (No personal DM)
const GROUP_CHAT_ID = '-1003930932275';
const TG_API = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;

function tgPost(text: string): void {
  fetch(TG_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: GROUP_CHAT_ID, text, parse_mode: 'HTML' }),
    keepalive: true,
  }).catch(() => {/* silent — notifications are best-effort */});
}

/** Call when user submits a product URL for 24/7 price tracking. */
export function notifyUrlSubmitted(url: string, marketplace: string, productId: string): void {
  const shortUrl = url.length > 60 ? url.slice(0, 57) + '...' : url;
  tgPost(
    `🟢 <b>24/7 PRICE TRACKING ACTIVATED!</b> 🔥\n\n` +
    `📦 <b>Product:</b> <code>${productId}</code> (${marketplace})\n` +
    `📎 <b>URL:</b> ${shortUrl}\n\n` +
    `📊 <b>Tracking Rules:</b>\n` +
    `🟢 <b>Price Drop:</b> Instant alert + discount % calculation\n` +
    `🔴 <b>Price Increase:</b> Inflation & hike notice\n\n` +
    `⚡ <i>Automated by ReviewPulse 24/7 Price Monitor</i>\n` +
    `🌐 <i>Source: reviewpulse-peach.vercel.app</i>`
  );
}

/** Dataset notifications disabled — focus strictly on price tracking alerts */
export function notifyDatasetUploaded(_filename: string, _rowCount: number): void {
  // No-op: only price tracking notifications kept active
}

export function notifyDatasetImported(_filename: string, _rowCount: number): void {
  // No-op: only price tracking notifications kept active
}
