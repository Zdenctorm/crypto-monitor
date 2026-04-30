#!/usr/bin/env python3
"""
crypto_monitor.py
Denní monitoring: CryptoPanic + Kraken/Coinbase/Binance/OKX announcements
Výstup: strukturovaný log soubor (Telegram later)
"""

import json
import logging
import re
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
    COINMARKETCAP_API_KEY,
)
from currency_contracts import TOKEN_CONTRACTS
from exchange_scraper import fetch_all_scrapers

# Precompilované regex patterny pro tokeny — sestaví se jednou při startu modulu.
# CASE-SENSITIVE: tickery jsou vždy UPPERCASE, ale slova jako "token", "not", "cloud"
# jsou lowercase → re.IGNORECASE by způsobovalo masivní false positives.
_TOKEN_PATTERNS: dict[str, re.Pattern] = {
    token: re.compile(rf'\b{re.escape(token)}\b')
    for token in TOKENS
}

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
    return [token for token, pat in _TOKEN_PATTERNS.items() if pat.search(text)]


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


_HIGH_REASONS = {
    "delist", "delisting", "removal", "will be removed", "trading pair removal",
    "suspend", "suspension", "halt", "trading halt", "discontinu",
    "wind down", "end of support", "trading stopped",
}
_MED_REASONS = {
    "migration", "migrate", "token swap", "chain migration", "network change",
    "network upgrade", "hard fork", "rebranding", "rebrand", "sunset", "deprecat",
}


def _priority_icon(reason: str) -> str:
    r = reason.lower()
    if any(h in r for h in _HIGH_REASONS):
        return "🔴"
    if any(m in r for m in _MED_REASONS):
        return "🟠"
    return "🟡"


def _priority_order(alert: dict) -> int:
    r = (alert.get("reason") or "").lower()
    if any(h in r for h in _HIGH_REASONS):
        return 0
    if any(m in r for m in _MED_REASONS):
        return 1
    return 2


def _send_telegram_summary(all_alerts: list[dict]):
    """
    Odešle 1 nebo více souhrnných zpráv (max 4000 znaků každá).
    Zabrání Telegram flood: místo N+1 zpráv jde vždy jen minimum zpráv.
    Alertů jsou seřazeny podle závažnosti: 🔴 delist > 🟠 migrace > 🟡 ostatní.
    """
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if not all_alerts:
        send_telegram(f"✅ <b>Crypto Monitor — {date_str}</b>\nŽádné nové relevantní zprávy.")
        return

    # Deduplikace přes uid
    seen_uids: set[str] = set()
    unique_alerts = []
    for a in all_alerts:
        if a["uid"] not in seen_uids:
            seen_uids.add(a["uid"])
            unique_alerts.append(a)

    # Seřadit: nejdříve kritické (delist/suspend), pak migrace, pak ostatní
    unique_alerts.sort(key=_priority_order)

    tokens_affected = {t for a in unique_alerts for t in (a["tokens"] or ["GENERAL"])}
    header = (
        f"🚨 <b>Crypto Monitor — {date_str}</b>\n"
        f"<b>{len(unique_alerts)}</b> alertů | tokeny: <b>{', '.join(sorted(tokens_affected))}</b>\n"
    )

    lines: list[str] = []
    for a in unique_alerts:
        icon = _priority_icon(a.get("reason", ""))
        tokens_str = ", ".join(a["tokens"]) if a["tokens"] else "GENERAL"
        title_short = a["title"][:100].rstrip()
        line = f"\n{icon} <b>[{tokens_str}]</b> — <i>{a['reason']}</i>\n"
        line += f"  {title_short}\n"
        line += f"  🏦 {a['source']}"
        if a.get("url"):
            line += f" | <a href=\"{a['url']}\">odkaz</a>"
        lines.append(line)

    # Rozdělíme na zprávy po max 4000 znacích
    LIMIT = 4000
    current = header
    for line in lines:
        if len(current) + len(line) + 1 > LIMIT:
            send_telegram(current)
            time.sleep(1)
            current = line + "\n"
        else:
            current += line + "\n"
    if current.strip():
        send_telegram(current)


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
            feed = feedparser.parse(
                feed_url,
                request_headers={"User-Agent": "Mozilla/5.0 (compatible; crypto-monitor/1.0; +https://github.com)"},
            )
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

            # Přeskočíme články bez konkrétního tokenu ze sledovaného seznamu
            if not tokens_found:
                continue

            alerts.append({
                "source":  exchange,
                "title":   title,
                "url":     url,
                "tokens":  tokens_found,
                "reason":  _extract_reason(full),
                "uid":     uid,
            })

    return alerts


def fetch_exchange_scrapers(seen_ids: set) -> list[dict]:
    """
    Scraping alternativa k RSS feedům.
    Používá JSON API (Binance, Bybit, Kraken) + HTML scraping (ostatní burzy).
    Aplikuje stejné filtrování klíčových slov a tokenů jako fetch_exchange_feeds().
    """
    alerts = []
    raw_items = fetch_all_scrapers()

    for item in raw_items:
        title  = item.get("title", "")
        url    = item.get("url", "")
        source = item.get("source", "scraper")
        full   = title
        uid    = item_id(url or title)

        if uid in seen_ids:
            continue

        if not contains_keyword(full):
            continue

        tokens_found = token_in_text(full)
        if not tokens_found:
            continue

        alerts.append({
            "source":  source,
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


# ── COINMARKETCAP ─────────────────────────────────────────────────────────────

CMC_MAP_URL  = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
CMC_INFO_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/info"

_CMC_HEADERS: dict = {}


def _cmc_headers() -> dict:
    return {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}


def _resolve_cmc_id_by_contract(token: str) -> int | None:
    """
    Pokusí se najít CMC ID tokenu pomocí contract adresy.
    Používá /v2/cryptocurrency/info?address=<addr>&network=<platform>.
    Vrátí první nalezené CMC ID nebo None.
    """
    contracts = TOKEN_CONTRACTS.get(token, [])
    for entry in contracts:
        platform = entry["platform"]
        address  = entry["address"]
        try:
            resp = requests.get(
                CMC_INFO_URL,
                headers=_cmc_headers(),
                params={"address": address, "network": platform},
                timeout=15,
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                # data is keyed by CMC ID
                for cmc_id_str, info in data.items():
                    return int(cmc_id_str)
        except Exception as e:
            log.debug("CMC contract lookup failed (%s %s): %s", token, address, e)
    return None


def fetch_coinmarketcap(seen_ids: set) -> list[dict]:
    """
    Zkontroluje, zda jsou sledované tokeny stále aktivní na CoinMarketCap.
    Pro tokeny se známou contract adresou používá přesné vyhledávání přes adresu,
    pro ostatní tokeny fallback na symbol matching přes /v1/cryptocurrency/map.
    Upozorní na tokeny označené jako neaktivní (is_active=0).
    """
    if not COINMARKETCAP_API_KEY:
        return []

    alerts = []

    # --- 1) Tokeny s contract adresou: přesné vyhledávání ---
    tokens_with_contracts = [t for t in TOKENS if t in TOKEN_CONTRACTS]
    tokens_without_contracts = [t for t in TOKENS if t not in TOKEN_CONTRACTS]

    log.debug("CMC: %d tokenů s contract adresou, %d bez", len(tokens_with_contracts), len(tokens_without_contracts))

    for token in tokens_with_contracts:
        try:
            cmc_id = _resolve_cmc_id_by_contract(token)
            if cmc_id is None:
                continue
            # Fetch status for resolved ID
            resp = requests.get(
                CMC_INFO_URL,
                headers=_cmc_headers(),
                params={"id": cmc_id},
                timeout=15,
            )
            resp.raise_for_status()
            info_data = resp.json().get("data", {})
            for id_str, info in info_data.items():
                is_active = info.get("is_active", 1)
                if is_active == 0:
                    uid = item_id(f"cmc-inactive-contract-{token}")
                    if uid not in seen_ids:
                        slug = info.get("slug", token.lower())
                        alerts.append({
                            "source": "CoinMarketCap",
                            "title":  f"{token} označen jako neaktivní na CoinMarketCap (ověřeno přes contract)",
                            "url":    f"https://coinmarketcap.com/currencies/{slug}/",
                            "tokens": [token],
                            "reason": "delist",
                            "uid":    uid,
                        })
        except Exception as e:
            log.error("CMC info fetch error (%s): %s", token, e)
        time.sleep(0.2)  # rate limit: free tier = 30 req/min

    # --- 2) Tokeny bez contract adresy: fallback přes symbol map ---
    if tokens_without_contracts:
        try:
            resp = requests.get(
                CMC_MAP_URL,
                headers=_cmc_headers(),
                params={"listing_status": "inactive,untracked", "limit": 5000},
                timeout=20,
            )
            resp.raise_for_status()
            map_data = resp.json()
        except Exception as e:
            log.error("CoinMarketCap map fetch error: %s", e)
            return alerts

        inactive_symbols = {
            entry["symbol"].upper()
            for entry in map_data.get("data", [])
            if entry.get("is_active") == 0
        }

        for token in tokens_without_contracts:
            if token not in inactive_symbols:
                continue
            uid = item_id(f"cmc-inactive-{token}")
            if uid in seen_ids:
                continue
            alerts.append({
                "source": "CoinMarketCap",
                "title":  f"{token} označen jako neaktivní na CoinMarketCap",
                "url":    f"https://coinmarketcap.com/currencies/{token.lower()}/",
                "tokens": [token],
                "reason": "delist",
                "uid":    uid,
            })

    return alerts


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
    log.info("Fetching exchange feeds (RSS)...")
    ex_alerts = fetch_exchange_feeds(seen_ids)
    log.info("  → %d nových alertů z exchange RSS feedů", len(ex_alerts))
    all_alerts.extend(ex_alerts)

    # 3) Exchange Web Scraping (záloha za RSS + burzy bez RSS)
    log.info("Fetching exchange feeds (web scraping)...")
    scrape_alerts = fetch_exchange_scrapers(seen_ids)
    log.info("  → %d nových alertů z web scrapingu", len(scrape_alerts))
    all_alerts.extend(scrape_alerts)

    # 4) CoinMarketCap (volitelné)
    if COINMARKETCAP_API_KEY:
        log.info("Fetching CoinMarketCap inactive tokens...")
        cmc_alerts = fetch_coinmarketcap(seen_ids)
        log.info("  → %d nových alertů z CoinMarketCap", len(cmc_alerts))
        all_alerts.extend(cmc_alerts)
    else:
        log.info("CoinMarketCap přeskočen (API key není nastaven)")

    # Deduplikace cross-source: stejný článek z RSS i JSON API scraperu má jiné URL
    # ale stejný titulek → normalizujeme titulek a zachováme jen první výskyt.
    seen_titles: set[str] = set()
    deduped: list[dict] = []
    for a in all_alerts:
        key = re.sub(r'\s+', ' ', a["title"].strip().lower())
        if key not in seen_titles:
            seen_titles.add(key)
            deduped.append(a)
    if len(deduped) < len(all_alerts):
        log.info("Cross-source dedup: %d → %d alertů", len(all_alerts), len(deduped))
    all_alerts = deduped

    # Logovat každý alert do souboru
    for a in all_alerts:
        log_alert(a["source"], a["title"], a["url"], a["tokens"], a["reason"])

    # Denní souhrn do logu
    log_summary(all_alerts)

    # Telegram: 1 souhrnná zpráva (nebo série zpráv po max 4000 znacích)
    _send_telegram_summary(all_alerts)

    # Uložit stav — seřadíme pro deterministické oříznutí na 5000 posledních
    new_ids = [a["uid"] for a in all_alerts]
    all_ids = sorted(seen_ids | set(new_ids))
    state["seen_ids"]  = all_ids[-5000:]
    state["last_run"]  = datetime.now(timezone.utc).isoformat()
    save_state(state)

    log.info("✔ Hotovo. Celkem %d alertů. Stav uložen.", len(all_alerts))


if __name__ == "__main__":
    main()
