#!/usr/bin/env python3
"""
crypto_monitor.py
Denní monitoring: CryptoPanic + Kraken/Coinbase/Binance/OKX announcements
Výstup: strukturovaný log soubor (Telegram later)
"""

import json
import logging
import time
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import requests
import feedparser

from config import (
    CRYPTOPANIC_API_KEY, TOKENS, KEYWORDS,
    EXCHANGE_FEEDS, STATE_FILE, LOG_FILE,
    TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID,
)

# ── LOGGING ──────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ── STATE ─────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    p = Path(STATE_FILE)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return {"seen_ids": [], "last_run": None}


def save_state(state: dict):
    Path(STATE_FILE).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def item_id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


# ── HELPERS ───────────────────────────────────────────────────────────────────

def contains_keyword(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in KEYWORDS)


def token_in_text(text: str) -> list[str]:
    """Vrátí seznam tokenů ze sledovaného seznamu, které se vyskytují v textu."""
    t = text.upper()
    found = []
    for token in TOKENS:
        # word-boundary check — vyhneme se falešným shodám (např. "CAR" v "CARBON")
        import re
        if re.search(rf'\b{re.escape(token)}\b', t):
            found.append(token)
    return found


def log_alert(source: str, title: str, url: str, tokens: list[str], reason: str):
    tokens_str = ", ".join(tokens) if tokens else "?"
    log.warning(
        "🚨 ALERT | source=%-10s | tokens=%-20s | reason=%-20s | %s | %s",
        source, tokens_str, reason, title[:80], url,
    )


def send_telegram(text: str):
    """Pošle zprávu přes Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        log.error("Telegram send error: %s", e)


# ── CRYPTOPANIC ───────────────────────────────────────────────────────────────

CRYPTOPANIC_URL = "https://cryptopanic.com/api/developer/v2/posts/"

def fetch_cryptopanic(seen_ids: set) -> list[dict]:
    """
    Stahuje zprávy z CryptoPanic pro všechny tokeny.
    Filtruje na klíčová slova a vrací nové položky.
    """
    alerts = []
    # API bere max ~50 currencies najednou — rozdělíme do dávek
    batch_size = 50
    token_list = list(TOKENS)

    for i in range(0, len(token_list), batch_size):
        batch = token_list[i:i + batch_size]
        currencies = ",".join(batch)
        params = {
            "auth_token": CRYPTOPANIC_API_KEY,
            "currencies": currencies,
            "filter": "important",   # hot/important zprávy
            "public": "true",
        }
        try:
            resp = requests.get(CRYPTOPANIC_URL, params=params, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.error("CryptoPanic fetch error (batch %d): %s", i // batch_size, e)
            time.sleep(2)
            continue

        for post in data.get("results", []):
            title = post.get("title", "")
            url   = post.get("url", "")
            uid   = item_id(url or title)

            if uid in seen_ids:
                continue

            # Kontrola klíčových slov
            if not contains_keyword(title):
                continue

            tokens_found = token_in_text(title)
            # Doplníme z currencies tagu pokud regex nic nenašel
            if not tokens_found:
                for c in post.get("currencies", []):
                    sym = c.get("code", "")
                    if sym in TOKENS:
                        tokens_found.append(sym)

            alerts.append({
                "source":  "CryptoPanic",
                "title":   title,
                "url":     url,
                "tokens":  tokens_found,
                "reason":  _extract_reason(title),
                "uid":     uid,
            })

        time.sleep(1)  # rate limit

    return alerts


# ── EXCHANGE RSS FEEDS ────────────────────────────────────────────────────────

def fetch_exchange_feeds(seen_ids: set) -> list[dict]:
    alerts = []

    for exchange, feed_url in EXCHANGE_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            log.error("Feed parse error (%s): %s", exchange, e)
            continue

        for entry in feed.entries:
            title   = entry.get("title", "")
            url     = entry.get("link", "")
            summary = entry.get("summary", "")
            full    = f"{title} {summary}"
            uid     = item_id(url or title)

            if uid in seen_ids:
                continue

            if not contains_keyword(full):
                continue

            tokens_found = token_in_text(full)

            # Pokud jsme nenašli žádný token ale article vypadá globálně důležitý
            # (např. "All ERC-20 tokens migration") — přidáme s tokens=[]
            alerts.append({
                "source":  exchange,
                "title":   title,
                "url":     url,
                "tokens":  tokens_found,
                "reason":  _extract_reason(full),
                "uid":     uid,
            })

    return alerts


def _extract_reason(text: str) -> str:
    """Najde první klíčové slovo v textu jako zkrácený důvod."""
    t = text.lower()
    for kw in KEYWORDS:
        if kw in t:
            return kw
    return "unknown"


# ── DAILY SUMMARY ─────────────────────────────────────────────────────────────

def log_summary(all_alerts: list[dict]):
    if not all_alerts:
        log.info("✅ Žádné nové relevantní zprávy dnes.")
        return

    log.info("=" * 70)
    log.info("📋 DENNÍ SOUHRN — %s — %d alertů",
             datetime.now(timezone.utc).strftime("%Y-%m-%d"), len(all_alerts))
    log.info("=" * 70)

    # Seskupit podle tokenu
    by_token: dict[str, list] = {}
    for a in all_alerts:
        for t in (a["tokens"] or ["GENERAL"]):
            by_token.setdefault(t, []).append(a)

    for token, items in sorted(by_token.items()):
        log.info("  [%s]", token)
        for item in items:
            log.info("    • [%s] %s", item["source"], item["title"][:100])
            log.info("      reason: %s | url: %s", item["reason"], item["url"])

    log.info("=" * 70)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    log.info("▶ Spouštím crypto_monitor — %s",
             datetime.now(timezone.utc).isoformat())

    state    = load_state()
    seen_ids = set(state.get("seen_ids", []))

    all_alerts = []

    # 1) CryptoPanic
    log.info("Fetching CryptoPanic...")
    cp_alerts = fetch_cryptopanic(seen_ids)
    log.info("  → %d nových alertů z CryptoPanic", len(cp_alerts))
    all_alerts.extend(cp_alerts)

    # 2) Exchange RSS feeds
    log.info("Fetching exchange feeds...")
    ex_alerts = fetch_exchange_feeds(seen_ids)
    log.info("  → %d nových alertů z exchange feedů", len(ex_alerts))
    all_alerts.extend(ex_alerts)

    # Logovat každý alert individuálně + poslat na Telegram
    for a in all_alerts:
        log_alert(a["source"], a["title"], a["url"], a["tokens"], a["reason"])
        tokens_str = ", ".join(a["tokens"]) if a["tokens"] else "GENERAL"
        msg = (
            f"🚨 <b>CRYPTO ALERT</b>\n"
            f"📌 <b>Token:</b> {tokens_str}\n"
            f"🏦 <b>Zdroj:</b> {a['source']}\n"
            f"⚠️ <b>Důvod:</b> {a['reason']}\n"
            f"📰 {a['title']}\n"
            f"🔗 <a href=\"{a['url']}\">Číst více</a>"
        )
        send_telegram(msg)

    # Denní souhrn
    log_summary(all_alerts)

    if all_alerts:
        summary_lines = [f"📋 <b>Denní souhrn — {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</b>"]
        summary_lines.append(f"Celkem {len(all_alerts)} alertů:\n")
        by_token: dict[str, list] = {}
        for a in all_alerts:
            for t in (a["tokens"] or ["GENERAL"]):
                by_token.setdefault(t, []).append(a)
        for token, items in sorted(by_token.items()):
            summary_lines.append(f"<b>[{token}]</b>")
            for item in items:
                summary_lines.append(f"  • [{item['source']}] {item['title'][:80]}")
        send_telegram("\n".join(summary_lines))
    else:
        send_telegram(f"✅ <b>Denní souhrn {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</b>\nŽádné nové relevantní zprávy.")

    # Uložit stav
    new_ids = [a["uid"] for a in all_alerts]
    # Limit na posledních 5000 ID abychom nepřetékali
    updated_ids = list(seen_ids | set(new_ids))[-5000:]
    state["seen_ids"]  = updated_ids
    state["last_run"]  = datetime.now(timezone.utc).isoformat()
    save_state(state)

    log.info("✔ Hotovo. Celkem %d alertů. Stav uložen.", len(all_alerts))


if __name__ == "__main__":
    main()
