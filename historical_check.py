#!/usr/bin/env python3
"""
historical_check.py
Jednorázová kontrola posledních N dní (výchozí: 30).

Zdroje (seřazeny podle důležitosti):
  1. Exchange RSS feedy  — oznámení burz o nadcházejících delistech/migracích
  2. CryptoPanic         — zpravodajské zdroje o nadcházejících delistech
  3. CoinMarketCap       — ověření tokenů, které JSOU JIŽ neaktivní (post-event)

Cíl: včasné upozornění PŘED delistingem/migrací, ne až poté.

Použití:
  python historical_check.py          # posledních 30 dní
  python historical_check.py 60       # posledních 60 dní
"""

import sys
import time
import os
import re
import requests
import feedparser
from datetime import datetime, timezone, timedelta

from config import TOKENS, KEYWORDS, EXCHANGE_FEEDS, COINMARKETCAP_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}
JSON_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

CRYPTOPANIC_API_KEY = os.environ.get("CRYPTOPANIC_API_KEY", "")
CMC_KEY             = os.environ.get("COINMARKETCAP_API_KEY", COINMARKETCAP_API_KEY)

DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 30
SINCE = datetime.now(timezone.utc) - timedelta(days=DAYS)

TOKENS_SET = set(TOKENS)


def send_telegram(text: str):
    """Pošle zprávu přes Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ⚠️  TELEGRAM_BOT_TOKEN nebo TELEGRAM_CHAT_ID není nastaven – přeskočeno")
        return
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
        print("  ✅ Zpráva odeslána do Telegramu")
    except Exception as e:
        print(f"  ❌ Telegram chyba: {e}")


def contains_keyword(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in KEYWORDS)


def first_keyword(text: str) -> str:
    t = text.lower()
    for kw in KEYWORDS:
        if kw in t:
            return kw
    return "?"


def find_tokens(text: str) -> list[str]:
    """Najde sledované tokeny v textu pomocí word-boundary regex."""
    found = []
    upper = text.upper()
    for token in TOKENS_SET:
        if re.search(rf'\b{re.escape(token)}\b', upper):
            found.append(token)
    return found


# ── 1) EXCHANGE RSS FEEDY (primární zdroj pre-delist oznámení) ────────────────

def fetch_exchange_feeds_history() -> list[dict]:
    """
    Prochází RSS feedy burz a hledá oznámení o nadcházejících delistech,
    migracích a jiných kritických událostech.

    RSS feedy typicky obsahují posledních 20–100 položek bez ohledu na datum.
    Filtrujeme na SINCE ale zobrazíme i starší pokud nejsou datovány
    (některé feedy datum neobsahují).
    """
    results = []
    print(f"  Procházím {len(EXCHANGE_FEEDS)} exchange feedů...")

    for exchange, feed_url in EXCHANGE_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url, request_headers=BROWSER_HEADERS)
        except Exception as e:
            print(f"    ⚠️  {exchange}: chyba parsování ({e})")
            continue

        if not feed.entries:
            print(f"    ⚠️  {exchange}: prázdný feed ({feed_url})")
            continue

        found_in_feed = 0
        for entry in feed.entries:
            title   = entry.get("title", "")
            url     = entry.get("link", "")
            summary = entry.get("summary", "") or ""
            full    = f"{title} {summary}"

            if not contains_keyword(full):
                continue

            # Zkus získat datum
            pub_date = None
            for date_field in ("published_parsed", "updated_parsed"):
                parsed = entry.get(date_field)
                if parsed:
                    try:
                        pub_date = datetime(*parsed[:6], tzinfo=timezone.utc)
                        break
                    except Exception:
                        pass

            # Přeskočit příliš staré záznamy (jen pokud datum víme)
            if pub_date and pub_date < SINCE:
                continue

            date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
            tokens_found = find_tokens(full)

            # Přeskočíme články bez konkrétního tokenu ze sledovaného seznamu
            if not tokens_found:
                continue

            results.append({
                "date":   date_str,
                "source": exchange,
                "tokens": tokens_found,
                "reason": first_keyword(full),
                "title":  title,
                "url":    url,
            })
            found_in_feed += 1

        print(f"    ✓  {exchange}: {found_in_feed} relevantních oznámení")

    return results


# ── 2) CRYPTOPANIC (zpravodajství o nadcházejících událostech) ─────────────────

def fetch_cryptopanic_history() -> list[dict]:
    """Stránkuje CryptoPanic dokud nenarazí na zprávy starší než SINCE."""
    if not CRYPTOPANIC_API_KEY:
        print("  ⚠️  CRYPTOPANIC_API_KEY není nastaven – přeskočeno")
        return []

    results = []
    next_url = None
    page = 0
    CRYPTOPANIC_URL = "https://cryptopanic.com/api/developer/v2/posts/"

    while True:
        page += 1
        try:
            if next_url:
                resp = requests.get(next_url, timeout=20)
            else:
                resp = requests.get(
                    CRYPTOPANIC_URL,
                    params={
                        "auth_token": CRYPTOPANIC_API_KEY,
                        "filter": "important",
                        "public": "true",
                        "kind": "news",
                    },
                    timeout=20,
                )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  ❌ CryptoPanic chyba (strana {page}): {e}")
            break

        posts = data.get("results", [])
        if not posts:
            break

        stop = False
        for post in posts:
            pub_raw = post.get("published_at", "")
            try:
                pub = datetime.fromisoformat(pub_raw.replace("Z", "+00:00"))
            except Exception:
                continue

            if pub < SINCE:
                stop = True
                break

            title = post.get("title", "")
            url   = post.get("url", "")

            if not contains_keyword(title):
                continue

            found_tokens = find_tokens(title)
            if not found_tokens:
                for c in post.get("currencies", []):
                    sym = c.get("code", "")
                    if sym in TOKENS_SET:
                        found_tokens.append(sym)

            # Přeskočíme zprávy bez konkrétního tokenu ze sledovaného seznamu
            if not found_tokens:
                continue

            results.append({
                "date":   pub.strftime("%Y-%m-%d"),
                "source": "CryptoPanic",
                "tokens": found_tokens,
                "reason": first_keyword(title),
                "title":  title,
                "url":    url,
            })

        if stop:
            print(f"  → dosaženo staré datum, zastaveno na straně {page}")
            break

        next_url = data.get("next")
        if not next_url:
            break

        print(f"  → zpracována strana {page}, nalezeno {len(results)} záznamů zatím...")
        time.sleep(1)

    return results


# ── 2b) EXCHANGE API ZDROJE (burzy bez funkčního RSS) ─────────────────────────

def fetch_binance_api_history() -> list[dict]:
    """Stahuje oznámení z Binance přes BAPI (catalogId=161 = delistingy)."""
    results = []
    BAPI_URL = "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query"
    headers = {**JSON_HEADERS, "Referer": "https://www.binance.com/"}
    seen_codes: set[str] = set()

    for params in [
        {"catalogId": "161", "pageNo": 1, "pageSize": 50},
        {"type": "1",        "pageNo": 1, "pageSize": 50},
    ]:
        try:
            resp = requests.get(BAPI_URL, params=params, headers=headers, timeout=20)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  ❌ Binance BAPI chyba: {e}")
            continue

        for article in data.get("data", {}).get("articles", []):
            code  = article.get("code", "")
            title = article.get("title", "")
            ts_ms = article.get("releaseDate", 0)
            url   = f"https://www.binance.com/en/support/announcement/{code}" if code else ""

            if code in seen_codes:
                continue
            seen_codes.add(code)

            try:
                pub_date = datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc)
            except Exception:
                pub_date = None

            if pub_date and pub_date < SINCE:
                continue

            if not contains_keyword(title):
                continue

            tokens_found = find_tokens(title)
            if not tokens_found:
                continue

            date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
            results.append({"date": date_str, "source": "Binance", "tokens": tokens_found,
                             "reason": first_keyword(title), "title": title, "url": url})

    return results


def fetch_okx_api_history() -> list[dict]:
    """Stahuje oznámení z OKX přes API v5."""
    results = []
    try:
        resp = requests.get(
            "https://www.okx.com/api/v5/support/announcements",
            params={"lang": "en-US", "limit": "50"},
            headers=JSON_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ❌ OKX API chyba: {e}")
        return results

    items = data.get("data", {})
    if isinstance(items, dict):
        items = items.get("list", [])
    if not isinstance(items, list):
        items = []

    for item in items:
        title = item.get("title", "")
        url   = item.get("url", "") or item.get("announcementUrl", "")
        ts    = item.get("pTime", "") or item.get("announcementPTime", "") or item.get("businessPTime", "")
        try:
            pub_date = datetime.fromtimestamp(int(ts) / 1000, tz=timezone.utc) if ts else None
        except Exception:
            pub_date = None

        if pub_date and pub_date < SINCE:
            continue
        if not contains_keyword(title):
            continue
        tokens_found = find_tokens(title)
        if not tokens_found:
            continue

        date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
        results.append({"date": date_str, "source": "OKX", "tokens": tokens_found,
                         "reason": first_keyword(title), "title": title, "url": url})
    return results


def fetch_kraken_support_history() -> list[dict]:
    """Stahuje oznámení z Kraken Support Centre přes Zendesk API."""
    results = []
    try:
        resp = requests.get(
            "https://support.kraken.com/api/v2/help_center/en-us/articles.json",
            params={"category_id": "200187583", "per_page": 50, "sort_by": "created_at", "sort_order": "desc"},
            headers=JSON_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ❌ KrakenSupport Zendesk API chyba: {e}")
        return results

    for article in data.get("articles", []):
        title    = article.get("title", "")
        url      = article.get("html_url", "")
        body     = article.get("body", "")
        created  = article.get("created_at", "")
        full     = f"{title} {body}"
        try:
            pub_date = datetime.fromisoformat(created.replace("Z", "+00:00")) if created else None
        except Exception:
            pub_date = None

        if pub_date and pub_date < SINCE:
            continue
        if not contains_keyword(full):
            continue
        tokens_found = find_tokens(full)
        if not tokens_found:
            continue

        date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
        results.append({"date": date_str, "source": "KrakenSupport", "tokens": tokens_found,
                         "reason": first_keyword(full), "title": title, "url": url})
    return results


def fetch_htx_api_history() -> list[dict]:
    """Stahuje oznámení z HTX přes Zendesk API."""
    results = []
    try:
        resp = requests.get(
            "https://support.htx.com/api/v2/help_center/en-us/articles.json",
            params={"per_page": 50, "sort_by": "created_at", "sort_order": "desc"},
            headers=JSON_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print(f"  ❌ HTX Zendesk API chyba: {e}")
        return results

    for article in data.get("articles", []):
        title    = article.get("title", "")
        url      = article.get("html_url", "")
        created  = article.get("created_at", "")
        try:
            pub_date = datetime.fromisoformat(created.replace("Z", "+00:00")) if created else None
        except Exception:
            pub_date = None

        if pub_date and pub_date < SINCE:
            continue
        if not contains_keyword(title):
            continue
        tokens_found = find_tokens(title)
        if not tokens_found:
            continue

        date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
        results.append({"date": date_str, "source": "HTX", "tokens": tokens_found,
                         "reason": first_keyword(title), "title": title, "url": url})
    return results


# ── 3) BYBIT API (announcement centrum bez RSS) ───────────────────────────────

def fetch_bybit_history() -> list[dict]:
    """
    Prochází Bybit V5 API a hledá oznámení v posledních DAYS dnech.
    Bybit nemá veřejné RSS (403), ale poskytuje dokumentované JSON API.
    """
    results = []
    page = 1
    BYBIT_URL = "https://api.bybit.com/v5/announcements/index"

    while True:
        try:
            resp = requests.get(
                BYBIT_URL,
                params={"locale": "en-US", "limit": 50, "page": page},
                timeout=20,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"  ❌ Bybit API chyba (strana {page}): {e}")
            break

        items = data.get("result", {}).get("list", [])
        if not items:
            break

        stop = False
        for item in items:
            ts_ms = item.get("dateTimestamp") or item.get("startDateTimestamp", 0)
            try:
                pub_date = datetime.fromtimestamp(int(ts_ms) / 1000, tz=timezone.utc)
            except Exception:
                pub_date = None

            if pub_date and pub_date < SINCE:
                stop = True
                break

            title       = item.get("title", "")
            description = item.get("description", "")
            url         = item.get("url", "")
            full        = f"{title} {description}"

            if not contains_keyword(full):
                continue

            tokens_found = find_tokens(full)
            if not tokens_found:
                continue

            date_str = pub_date.strftime("%Y-%m-%d") if pub_date else "datum neznámé"
            results.append({
                "date":   date_str,
                "source": "Bybit",
                "tokens": tokens_found,
                "reason": first_keyword(full),
                "title":  title,
                "url":    url,
            })

        if stop:
            print(f"  → dosaženo staré datum, zastaveno na straně {page}")
            break

        total = data.get("result", {}).get("total", 0)
        if page * 50 >= total:
            break

        page += 1
        time.sleep(0.3)

    return results


# ── 4) COINMARKETCAP (ověření tokenů které JIŽ jsou neaktivní) ────────────────

def fetch_cmc_inactive() -> list[dict]:
    """
    Vrátí tokeny ze sledovaného seznamu, které nemají žádnou aktivní položku na CMC.

    POZOR: Toto je POST-event ověření — token je zde až POTÉ, co byl delistován.
    Slouží jako záchranná síť pro případy, kdy jsme propásli předchozí oznámení.

    Ticker symbol může sdílet více různých coinů (aktivních i neaktivních).
    Token hlásíme jako neaktivní pouze tehdy, pokud pro daný symbol neexistuje
    žádná aktivní položka.
    """
    if not CMC_KEY:
        print("  ⚠️  COINMARKETCAP_API_KEY není nastaven – přeskočeno")
        return []

    def fetch_map(listing_status: str) -> list[dict]:
        results = []
        start = 1
        limit = 5000
        while True:
            try:
                resp = requests.get(
                    "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
                    headers={"X-CMC_PRO_API_KEY": CMC_KEY},
                    params={"listing_status": listing_status, "limit": limit, "start": start},
                    timeout=20,
                )
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                print(f"  ❌ CoinMarketCap chyba ({listing_status}, start={start}): {e}")
                break
            page = data.get("data", [])
            results.extend(page)
            if len(page) < limit:
                break
            start += limit
        return results

    active_symbols: set[str] = set()
    for entry in fetch_map("active"):
        sym = entry.get("symbol", "").upper()
        if sym in TOKENS_SET:
            active_symbols.add(sym)

    seen_inactive: dict[str, dict] = {}
    for entry in fetch_map("inactive,untracked"):
        sym = entry.get("symbol", "").upper()
        if sym not in TOKENS_SET or sym in active_symbols:
            continue
        if sym not in seen_inactive:
            seen_inactive[sym] = entry

    inactive = []
    for sym, entry in seen_inactive.items():
        inactive.append({
            "date":   "aktuální stav (post-delist)",
            "source": "CoinMarketCap",
            "tokens": [sym],
            "reason": "inactive/delist",
            "title":  f"{sym} – žádná aktivní položka na CoinMarketCap (delist již proběhl)",
            "url":    f"https://coinmarketcap.com/currencies/{entry.get('slug', sym.lower())}/",
        })
    return inactive


# ── VÝSTUP ────────────────────────────────────────────────────────────────────

def print_results(results: list[dict], heading: str):
    if not results:
        print(f"\n  ✅ {heading}: Žádné záznamy nenalezeny.")
        return

    results.sort(key=lambda x: x["date"], reverse=True)

    by_token: dict[str, list] = {}
    for r in results:
        for t in (r["tokens"] or ["GENERAL"]):
            by_token.setdefault(t, []).append(r)

    print(f"\n  {heading} — {len(results)} záznamů pro {len(by_token)} tokenů:\n")
    for token in sorted(by_token):
        print(f"  ┌─ [{token}]")
        for item in by_token[token]:
            print(f"  │  📅 {item['date']}  [{item['source']}]  reason: {item['reason']}")
            print(f"  │     {item['title'][:90]}")
            print(f"  │     {item['url']}")
        print("  │")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print(f"  CRYPTO MONITOR — HISTORICKÁ KONTROLA (posledních {DAYS} dní)")
    print(f"  Od: {SINCE.strftime('%Y-%m-%d')} do: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print("=" * 65)

    # ── 1) Exchange feedy (pre-delist oznámení) ───────────────────────────────
    print(f"\n🏦 Exchange feedy (oznámení o nadcházejících delistech/migracích):")
    exchange_results = fetch_exchange_feeds_history()
    print(f"  → celkem {len(exchange_results)} relevantních oznámení z burz")

    # ── 2b) Exchange API zdroje (burzy bez funkčního RSS) ────────────────────
    print(f"\n🔌 Exchange API zdroje (burzy bez RSS):")
    binance_results = fetch_binance_api_history()
    print(f"  → Binance BAPI: {len(binance_results)} oznámení")

    okx_results = fetch_okx_api_history()
    print(f"  → OKX API v5: {len(okx_results)} oznámení")

    kraken_support_results = fetch_kraken_support_history()
    print(f"  → KrakenSupport Zendesk: {len(kraken_support_results)} oznámení")

    htx_results = fetch_htx_api_history()
    print(f"  → HTX Zendesk: {len(htx_results)} oznámení")

    # ── 2c) Bybit API ────────────────────────────────────────────────────────
    print(f"\n🟡 Bybit API (oznámení, stránkování {DAYS} dní):")
    bybit_results = fetch_bybit_history()
    print(f"  → celkem {len(bybit_results)} relevantních oznámení")

    # ── 3) CryptoPanic (pre-delist zprávy) ───────────────────────────────────
    print(f"\n📰 CryptoPanic (zprávy o nadcházejících událostech, stránkování {DAYS} dní):")
    cp_results = fetch_cryptopanic_history()
    print(f"  → celkem {len(cp_results)} relevantních zpráv")

    # ── 4) CoinMarketCap (post-delist ověření) ────────────────────────────────
    print(f"\n📊 CoinMarketCap (tokeny které JIŽ jsou neaktivní — post-event ověření):")
    cmc_results = fetch_cmc_inactive()
    print(f"  → celkem {len(cmc_results)} tokenů bez aktivní položky na CMC")

    # ── Výpis ─────────────────────────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("  VÝSLEDKY")
    print("=" * 65)

    print_results(exchange_results,       "🏦 OZNÁMENÍ BURZ – RSS (pre-delist/migrace)")
    print_results(binance_results,        "🟠 BINANCE API")
    print_results(okx_results,            "🔵 OKX API")
    print_results(kraken_support_results, "🐙 KRAKEN SUPPORT (Zendesk API)")
    print_results(htx_results,            "🟣 HTX (Zendesk API)")
    print_results(bybit_results,          "🟡 BYBIT API")
    print_results(cp_results,             "📰 CRYPTOPANIC (zprávy o kritických událostech)")
    print_results(cmc_results,            "📊 COINMARKETCAP (již delistované tokeny)")

    print("=" * 65)

    # ── Telegram notifikace ───────────────────────────────────────────────────
    print("\n📨 Odesílám výsledky do Telegramu...")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    pre_event = exchange_results + binance_results + okx_results + kraken_support_results + htx_results + bybit_results + cp_results
    if not pre_event and not cmc_results:
        send_telegram(
            f"✅ <b>Historická kontrola {date_str} (posledních {DAYS} dní)</b>\n"
            "Žádné záznamy o nadcházejících ani proběhlých delistech/migracích."
        )
        return

    # Úvodní souhrn
    lines = [
        f"🔍 <b>Historická kontrola {date_str} (posledních {DAYS} dní)</b>",
        f"🏦 RSS feedy: <b>{len(exchange_results)}</b>",
        f"🟠 Binance API: <b>{len(binance_results)}</b>",
        f"🔵 OKX API: <b>{len(okx_results)}</b>",
        f"🐙 KrakenSupport: <b>{len(kraken_support_results)}</b>",
        f"🟣 HTX API: <b>{len(htx_results)}</b>",
        f"🟡 Bybit API: <b>{len(bybit_results)}</b>",
        f"📰 CryptoPanic: <b>{len(cp_results)}</b>",
        f"📊 CMC neaktivní (post-delist): <b>{len(cmc_results)}</b>",
    ]
    send_telegram("\n".join(lines))

    # Detaily: nejprve pre-event (burzy + cryptopanic), pak post-event (CMC)
    for section_label, items in [
        ("🏦 RSS burzy",      exchange_results),
        ("🟠 Binance",        binance_results),
        ("🔵 OKX",            okx_results),
        ("🐙 KrakenSupport",  kraken_support_results),
        ("🟣 HTX",            htx_results),
        ("🟡 Bybit",          bybit_results),
        ("📰 CryptoPanic",    cp_results),
        ("📊 CMC (post-delist)", cmc_results),
    ]:
        for r in sorted(items, key=lambda x: x["date"], reverse=True):
            tokens_str = ", ".join(r["tokens"]) if r["tokens"] else "GENERAL"
            msg = (
                f"{section_label}\n"
                f"🪙 <b>[{tokens_str}]</b> – {r['reason']}\n"
                f"📅 {r['date']} | {r['source']}\n"
                f"{r['title'][:200]}\n"
                f"{r['url']}"
            )
            send_telegram(msg)
            time.sleep(0.3)


if __name__ == "__main__":
    main()
