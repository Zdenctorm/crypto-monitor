#!/usr/bin/env python3
"""
health_check.py
Ověří dostupnost všech zdrojů (RSS feedy, JSON API scrapery, CryptoPanic, Telegram).
Spouštěj ručně nebo automaticky před monitorem v GitHub Actions.

Výstup:
  ✅ zdroj OK
  ❌ zdroj selhal     → workflow skončí s exit code 1  (povinný zdroj)
  ⚠️  zdroj selhal    → jen varování, workflow pokračuje (volitelný zdroj)

Architektura zdrojů:
  Povinné RSS feedy   → Binance, BinanceDelisting, Kraken blog, KuCoin news
  Povinné scrapery    → Bybit, KuCoin, Gate, Binance (JSON API)
  Volitelné scrapery  → Kraken support, HTX, OKX, CryptoCom, Coinbase help
  Telegram kanály     → záloha pro burzy bez funkčního API (všechny volitelné)
  API zdroje          → CryptoPanic (povinný), CoinMarketCap (volitelný)
"""

import os
import sys
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
    scrape_coinbase,
    scrape_coinbase_help,
    scrape_telegram_bybit,
    scrape_telegram_okx,
    scrape_telegram_gate,
    scrape_telegram_cryptocom,
    scrape_telegram_htx,
)

CRYPTOPANIC_API_KEY   = os.environ.get("CRYPTOPANIC_API_KEY", "")
TELEGRAM_BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID      = os.environ.get("TELEGRAM_CHAT_ID", "")
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")


def check_feed(name: str, url: str) -> bool:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; crypto-monitor/1.0)"})
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        entry_count = len(feed.entries)
        if feed.bozo and entry_count == 0:
            print(f"  ❌ {name}: prázdný nebo chybný feed ({feed.bozo_exception})")
            return False
        print(f"  ✅ {name}: OK ({entry_count} položek)")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ {name}: HTTP {e.response.status_code} – {url}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"  ❌ {name}: nelze se připojit – {url}")
        return False
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        return False


def check_scraper(name: str, scraper_fn, *, optional: bool = False) -> bool:
    """
    Zavolá scraper funkci a ověří že vrátila alespoň 1 položku.
    Scraper musí vrátit list[dict] s klíčem 'title'.
    """
    try:
        items = scraper_fn()
        count = len(items)
        if count > 0:
            sample = items[0].get("title", "")[:60]
            print(f"  ✅ {name}: OK ({count} položek, např. \"{sample}...\")")
            return True
        else:
            prefix = "⚠️ " if optional else "❌"
            print(f"  {prefix} {name}: scraper vrátil 0 položek")
            return False
    except Exception as e:
        prefix = "⚠️ " if optional else "❌"
        print(f"  {prefix} {name}: {e}")
        return False


def check_cryptopanic() -> bool:
    if not CRYPTOPANIC_API_KEY:
        print("  ❌ CryptoPanic: API key není nastaven (CRYPTOPANIC_API_KEY)")
        return False
    try:
        resp = requests.get(
            "https://cryptopanic.com/api/developer/v2/posts/",
            params={"auth_token": CRYPTOPANIC_API_KEY, "public": "true", "limit": 1},
            timeout=15,
        )
        resp.raise_for_status()
        count = len(resp.json().get("results", []))
        print(f"  ✅ CryptoPanic: OK ({count} výsledků v odpovědi)")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ CryptoPanic: HTTP {e.response.status_code} – špatný API key?")
        return False
    except Exception as e:
        print(f"  ❌ CryptoPanic: {e}")
        return False


def check_telegram() -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("  ❌ Telegram: TELEGRAM_BOT_TOKEN nebo TELEGRAM_CHAT_ID není nastaven")
        return False
    try:
        resp = requests.get(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe",
            timeout=10,
        )
        resp.raise_for_status()
        bot_name = resp.json().get("result", {}).get("username", "?")
        print(f"  ✅ Telegram: OK (bot @{bot_name})")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Telegram: HTTP {e.response.status_code} – špatný bot token?")
        return False
    except Exception as e:
        print(f"  ❌ Telegram: {e}")
        return False


def check_coinmarketcap() -> bool | None:
    """Vrátí None pokud není API key (volitelné), True/False jinak."""
    if not COINMARKETCAP_API_KEY:
        print("  ⚠️  CoinMarketCap: API key není nastaven (volitelné, přeskočeno)")
        return None
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
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ CoinMarketCap: HTTP {e.response.status_code} – špatný API key?")
        return False
    except Exception as e:
        print(f"  ❌ CoinMarketCap: {e}")
        return False


def send_telegram_alert(required_failed: list[str], optional_failed_count: int = 0):
    """
    Pošle Telegram zprávu pouze o selhání povinných zdrojů.
    Volitelné zdroje se do Telegramu nezasílají — jejich selhání je v GitHub Actions logu.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    lines = ["⚠️ <b>Health Check – nefunkční povinné zdroje</b>"]
    for name in required_failed:
        lines.append(f"  ❌ {name}")
    if optional_failed_count > 0:
        lines.append(f"\n<i>+ {optional_failed_count} volitelných zdrojů selhalo (viz GitHub Actions log)</i>")
    lines.append("\nZkontroluj GitHub Actions log.")
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": "\n".join(lines), "parse_mode": "HTML"},
            timeout=10,
        )
    except Exception:
        pass


def main():
    print("=" * 60)
    print("  CRYPTO MONITOR — HEALTH CHECK")
    print("=" * 60)

    required_failed: list[str] = []   # povinné — blokují workflow + Telegram alert
    optional_failed: list[str] = []   # volitelné — jen stdout log, bez Telegramu
    required_results: list[bool] = []

    # ── RSS feedy (jen ty které stále fungují) ───────────────────
    print("\n📡 RSS Feedy (povinné):")
    for name, url in EXCHANGE_FEEDS.items():
        ok = check_feed(name, url)
        required_results.append(ok)
        if not ok:
            required_failed.append(name)

    # ── JSON API scrapery (primární zdroj dat) ───────────────────
    print("\n🔌 JSON API Scrapery (povinné):")
    mandatory_scrapers = [
        ("Binance JSON API", scrape_binance),
        ("KuCoin v3 API",    scrape_kucoin),
    ]
    for name, fn in mandatory_scrapers:
        ok = check_scraper(name, fn)
        required_results.append(ok)
        if not ok:
            required_failed.append(name)

    # Bybit a Gate.io jsou volitelné — jejich API je blokováno Cloudflare
    # z GitHub Actions IP; data sbíráme přes Telegram kanály jako zálohu.
    print("\n🔌 JSON API Scrapery (volitelné):")
    optional_scrapers = [
        ("Bybit JSON API",         scrape_bybit),
        ("Gate.io JSON API",       scrape_gate),
        ("Kraken Support Zendesk", scrape_kraken),
        ("HTX Zendesk API",        scrape_htx),
        ("OKX SSR JSON",           scrape_okx),
        ("Crypto.com POST API",    scrape_cryptocom),
        ("Coinbase blog RSS",      scrape_coinbase),
        ("Coinbase Help Zendesk",  scrape_coinbase_help),
    ]
    for name, fn in optional_scrapers:
        ok = check_scraper(name, fn, optional=True)
        if not ok:
            print(f"     ↳ {name} selhal – volitelný scraper, monitor pokračuje")
            optional_failed.append(name)

    # ── Telegram kanály (záloha pro burzy bez API) ───────────────
    # Gate a HTX vynecháme z health checku — kanály jsou nestabilní / přejmenované.
    # Scraper je stále zkouší, ale selhání nehlásíme do Telegramu.
    print("\n📣 Telegram Kanály (volitelné zálohy):")
    telegram_scrapers = [
        ("Telegram/Bybit",     scrape_telegram_bybit),
        ("Telegram/OKX",       scrape_telegram_okx),
        ("Telegram/CryptoCom", scrape_telegram_cryptocom),
    ]
    for name, fn in telegram_scrapers:
        ok = check_scraper(name, fn, optional=True)
        if not ok:
            print(f"     ↳ {name} selhal – Telegram záloha, monitor pokračuje")
            optional_failed.append(name)

    # ── API zdroje ───────────────────────────────────────────────
    print("\n🔑 API Zdroje:")
    cp_ok = check_cryptopanic()
    required_results.append(cp_ok)
    if not cp_ok:
        required_failed.append("CryptoPanic API")
    check_coinmarketcap()   # volitelné, neblokuje workflow

    # ── Telegram bot ─────────────────────────────────────────────
    print("\n📬 Telegram Bot:")
    tg_ok = check_telegram()
    required_results.append(tg_ok)

    # ── Výsledek ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    if optional_failed:
        print(f"  ⚠️  {len(optional_failed)} volitelných zdrojů selhalo: {', '.join(optional_failed)}")

    failed = sum(1 for r in required_results if r is False)
    total  = len(required_results)
    ok_count = total - failed

    if failed:
        print(f"  ❌ SELHALO {failed}/{total} povinných zdrojů – zkontroluj výstup výše")
        print("=" * 60)
        if tg_ok and required_failed:
            send_telegram_alert(required_failed, len(optional_failed))
        sys.exit(1)
    else:
        print(f"  ✅ Všechny povinné zdroje fungují ({ok_count}/{total})")
        print("=" * 60)


if __name__ == "__main__":
    main()
