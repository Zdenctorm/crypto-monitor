#!/usr/bin/env python3
"""
health_check.py
Informační test dostupnosti zdrojů — výsledek jde jen do GitHub Actions logu,
NIKDY ne do Telegramu. Monitor se spustí i při selhání všech zdrojů.

Účel: zjistit které scrapery fungují z GitHub Actions IP, ne blokovat workflow.
"""

import os
import requests
import feedparser

from config import EXCHANGE_FEEDS
from exchange_scraper import (
    scrape_binance,
    scrape_bybit,
    scrape_kraken,
    scrape_kucoin,
    scrape_htx,
    scrape_cryptocom,
    scrape_okx,
    scrape_gate,
    scrape_mexc,
    scrape_coinbase,
    scrape_coinbase_help,
)

CRYPTOPANIC_API_KEY   = os.environ.get("CRYPTOPANIC_API_KEY", "")
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")


def check_feed(name: str, url: str) -> bool:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; crypto-monitor/1.0)"})
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        entry_count = len(feed.entries)
        if feed.bozo and entry_count == 0:
            print(f"  ❌ {name}: prázdný nebo chybný feed")
            return False
        print(f"  ✅ {name}: OK ({entry_count} položek)")
        return True
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False


def check_scraper(name: str, scraper_fn) -> bool:
    try:
        items = scraper_fn()
        count = len(items)
        if count > 0:
            sample = items[0].get("title", "")[:60]
            print(f"  ✅ {name}: OK ({count} položek, např. \"{sample}...\")")
            return True
        else:
            print(f"  ⚠️  {name}: 0 položek")
            return False
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False


def check_cryptopanic() -> bool:
    if not CRYPTOPANIC_API_KEY:
        print("  ⚠️  CryptoPanic: API key není nastaven (přeskočeno)")
        return False
    try:
        resp = requests.get(
            "https://cryptopanic.com/api/developer/v2/posts/",
            params={"auth_token": CRYPTOPANIC_API_KEY, "public": "true", "limit": 1},
            timeout=15,
        )
        resp.raise_for_status()
        count = len(resp.json().get("results", []))
        print(f"  ✅ CryptoPanic: OK ({count} výsledků)")
        return True
    except Exception as e:
        print(f"  ❌ CryptoPanic: {e}")
        return False


def check_coinmarketcap() -> bool:
    if not COINMARKETCAP_API_KEY:
        print("  ⚠️  CoinMarketCap: API key není nastaven (přeskočeno)")
        return False
    try:
        resp = requests.get(
            "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map",
            headers={"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY},
            params={"limit": 1},
            timeout=15,
        )
        resp.raise_for_status()
        print("  ✅ CoinMarketCap: OK")
        return True
    except Exception as e:
        print(f"  ❌ CoinMarketCap: {e}")
        return False


def main():
    print("=" * 60)
    print("  CRYPTO MONITOR — HEALTH CHECK (jen log, bez Telegram alertů)")
    print("=" * 60)

    ok_count = 0
    total = 0

    # ── RSS feedy ────────────────────────────────────────────────
    print("\n📡 RSS Feedy:")
    for name, url in EXCHANGE_FEEDS.items():
        total += 1
        if check_feed(name, url):
            ok_count += 1

    # ── JSON API scrapery ─────────────────────────────────────────
    print("\n🔌 JSON API Scrapery:")
    scrapers = [
        ("Binance JSON API",       scrape_binance),
        ("KuCoin v3 API",          scrape_kucoin),
        ("Bybit API",              scrape_bybit),
        ("Gate.io API",            scrape_gate),
        ("Kraken Support Zendesk", scrape_kraken),
        ("HTX Zendesk",            scrape_htx),
        ("OKX SSR",                scrape_okx),
        ("Crypto.com API",         scrape_cryptocom),
        ("MEXC API",               scrape_mexc),
        ("Coinbase blog RSS",      scrape_coinbase),
        ("Coinbase Help Zendesk",  scrape_coinbase_help),
    ]
    for name, fn in scrapers:
        total += 1
        if check_scraper(name, fn):
            ok_count += 1

    # ── API zdroje ───────────────────────────────────────────────
    print("\n🔑 API Zdroje:")
    total += 1
    if check_cryptopanic():
        ok_count += 1
    check_coinmarketcap()

    # ── Výsledek (jen log, žádný sys.exit, žádný Telegram) ───────
    print("\n" + "=" * 60)
    print(f"  Výsledek: {ok_count}/{total} zdrojů funkčních")
    print("  (Selhání zdrojů neblokuje monitor — viz monitor.log pro výsledky)")
    print("=" * 60)


if __name__ == "__main__":
    main()
