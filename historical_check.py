#!/usr/bin/env python3
"""
historical_check.py
Jednorázová kontrola posledních N dní (výchozí: 30).
Prochází CryptoPanic historii stránku po stránce a CoinMarketCap neaktivní tokeny.
Nevyužívá seen_ids – zobrazí vše co se za období stalo.

Použití:
  python historical_check.py          # posledních 30 dní
  python historical_check.py 60       # posledních 60 dní
"""

import sys
import time
import os
import requests
from datetime import datetime, timezone, timedelta

from config import TOKENS, KEYWORDS, COINMARKETCAP_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

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

            # tokeny z textu nebo z currencies tagu
            import re
            found_tokens = [
                t for t in TOKENS_SET
                if re.search(rf'\b{re.escape(t)}\b', title.upper())
            ]
            if not found_tokens:
                for c in post.get("currencies", []):
                    sym = c.get("code", "")
                    if sym in TOKENS_SET:
                        found_tokens.append(sym)

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


def fetch_cmc_inactive() -> list[dict]:
    """Vrátí tokeny ze sledovaného seznamu, které nemají žádnou aktivní položku na CMC.

    Ticker symbol může sdílet více různých coinů (aktivních i neaktivních).
    Token hlásíme jako neaktivní pouze tehdy, pokud pro daný symbol neexistuje
    žádná aktivní položka – tj. i původně sledovaný coin byl delistován.
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

    # Symboly, které mají alespoň jednu aktivní položku na CMC
    active_symbols: set[str] = set()
    for entry in fetch_map("active"):
        sym = entry.get("symbol", "").upper()
        if sym in TOKENS_SET:
            active_symbols.add(sym)

    # Neaktivní / untracked položky – zajímají nás jen ty, jejichž symbol
    # VŮBEC nemá aktivní protějšek (jinak jde o starý coin se stejným tickerem)
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
            "date":   "aktuální stav",
            "source": "CoinMarketCap",
            "tokens": [sym],
            "reason": "inactive/delist",
            "title":  f"{sym} – žádná aktivní položka na CoinMarketCap",
            "url":    f"https://coinmarketcap.com/currencies/{entry.get('slug', sym.lower())}/",
        })
    return inactive


def print_results(results: list[dict]):
    if not results:
        print("\n  ✅ Žádné záznamy o migracích/delistinzích nenalezeny.")
        return

    # Seřadit podle data sestupně
    results.sort(key=lambda x: x["date"], reverse=True)

    # Skupinovat po tokenech
    by_token: dict[str, list] = {}
    for r in results:
        for t in (r["tokens"] or ["GENERAL"]):
            by_token.setdefault(t, []).append(r)

    print(f"\n  Nalezeno {len(results)} záznamů pro {len(by_token)} tokenů:\n")
    for token in sorted(by_token):
        print(f"  ┌─ [{token}]")
        for item in by_token[token]:
            print(f"  │  📅 {item['date']}  [{item['source']}]  reason: {item['reason']}")
            print(f"  │     {item['title'][:90]}")
            print(f"  │     {item['url']}")
        print("  │")


def main():
    print("=" * 65)
    print(f"  CRYPTO MONITOR — HISTORICKÁ KONTROLA (posledních {DAYS} dní)")
    print(f"  Od: {SINCE.strftime('%Y-%m-%d')} do: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print("=" * 65)

    all_results = []

    print(f"\n📰 CryptoPanic (stránkování zpět {DAYS} dní):")
    cp = fetch_cryptopanic_history()
    print(f"  → celkem {len(cp)} relevantních zpráv")
    all_results.extend(cp)

    print(f"\n📊 CoinMarketCap (aktuálně neaktivní tokeny ze sledovaného seznamu):")
    cmc = fetch_cmc_inactive()
    print(f"  → celkem {len(cmc)} neaktivních tokenů ze sledovaného seznamu")
    all_results.extend(cmc)

    print("\n" + "=" * 65)
    print("  VÝSLEDKY")
    print("=" * 65)
    print_results(all_results)
    print("=" * 65)

    # ── Telegram notifikace ──────────────────────────────────────────────────
    print("\n📨 Odesílám výsledky do Telegramu...")
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not all_results:
        send_telegram(
            f"✅ <b>Historická kontrola {date_str} (posledních {DAYS} dní)</b>\n"
            "Žádné záznamy o migracích/delistinzích nenalezeny."
        )
    else:
        # Úvodní zpráva se souhrnem
        send_telegram(
            f"🔍 <b>Historická kontrola {date_str} (posledních {DAYS} dní)</b>\n"
            f"Nalezeno <b>{len(all_results)}</b> záznamů. Posílám detaily..."
        )
        # Každý záznam jako samostatná zpráva (Telegram limit 4096 znaků)
        for r in sorted(all_results, key=lambda x: x["date"], reverse=True):
            tokens_str = ", ".join(r["tokens"]) if r["tokens"] else "GENERAL"
            msg = (
                f"🚨 <b>[{tokens_str}]</b> – {r['reason']}\n"
                f"📅 {r['date']} | {r['source']}\n"
                f"{r['title'][:200]}\n"
                f"{r['url']}"
            )
            send_telegram(msg)
            time.sleep(0.3)  # rate limit


if __name__ == "__main__":
    main()
