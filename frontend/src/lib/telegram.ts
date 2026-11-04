/**
 * Lightweight fire-and-forget Telegram notifier for website actions.
 * Sends a push notification to the owner's phone via Telegram Bot API
 * whenever a user submits a URL or uploads a dataset on the website.
 *
 * Uses fetch() with keepalive so it fires even on page navigation.
 * No secrets are truly hidden in a frontend app — this is acceptable since
 * the bot token only allows sending messages to a specific chat_id.
 */

const BOT_TOKEN = '9149329197:AAEMiSz8nhY0Oc-BCPVgo5xJfN2kMHPTFSw';
const CHAT_ID = '7154556693';
const TG_API = `https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`;

function tgPost(text: string): void {
  fetch(TG_API, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chat_id: CHAT_ID, text, parse_mode: 'HTML' }),
    keepalive: true,
  }).catch(() => {/* silent — notifications are best-effort */});
}

/** Call when user submits a product URL from the website. */
export function notifyUrlSubmitted(url: string, marketplace: string, productId: string): void {
  const shortUrl = url.length > 60 ? url.slice(0, 57) + '...' : url;
  tgPost(
    `🌐 <b>NEW URL SUBMITTED via ReviewPulse Website!</b>\n\n` +
    `🔗 <b>Marketplace:</b> ${marketplace}\n` +
    `🆔 <b>Product ID:</b> <code>${productId}</code>\n` +
    `📎 <b>URL:</b> ${shortUrl}\n\n` +
    `⚡ <i>ReviewPulse is analyzing this product now...</i>\n` +
    `🌐 <i>Source: reviewpulse-peach.vercel.app</i>`
  );
}

/** Call when user uploads a dataset file on the website. */
export function notifyDatasetUploaded(filename: string, rowCount: number): void {
  tgPost(
    `📁 <b>DATASET UPLOADED via ReviewPulse Website!</b>\n\n` +
    `📊 <b>File:</b> <code>${filename}</code>\n` +
    `📋 <b>Detected Rows:</b> <b>${rowCount.toLocaleString('en-IN')}</b>\n\n` +
    `🧠 <i>ReviewPulse NLP is processing sentiment & ratings...</i>\n` +
    `🌐 <i>Source: reviewpulse-peach.vercel.app</i>`
  );
}

/** Call when dataset import completes successfully on the website. */
export function notifyDatasetImported(filename: string, rowCount: number): void {
  tgPost(
    `✅ <b>DATASET IMPORT COMPLETE!</b>\n\n` +
    `📁 <b>File:</b> <code>${filename}</code>\n` +
    `📊 <b>Rows Processed:</b> <b>${rowCount.toLocaleString('en-IN')}</b>\n` +
    `📈 <b>Status:</b> Reviews now active in workspace library\n\n` +
    `⚡ <i>ReviewPulse Neural Engine — reviewpulse-peach.vercel.app</i>`
  );
}
