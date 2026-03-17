#!/usr/bin/env python3
"""
health_check.py
Ověří dostupnost všech zdrojů (RSS feedy, CryptoPanic API, CoinMarketCap, Telegram).
Spouštěj ručně nebo automaticky před monitorem v GitHub Actions.

Výstup:
  ✅ zdroj OK
  ❌ zdroj selhal  → workflow skončí s exit code 1
  ⚠️  zdroj přeskočen (chybí API key – volitelné)
"""

import os
import sys
import requests
import feedparser

# Přímý import aby health_check fungoval i bez nastavených env vars
from config import EXCHANGE_FEEDS

CRYPTOPANIC_API_KEY   = os.environ.get("CRYPTOPANIC_API_KEY", "")
TELEGRAM_BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID      = os.environ.get("TELEGRAM_CHAT_ID", "")
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")


def check_feed(name: str, url: str) -> bool:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "crypto-monitor/1.0"})
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


def main():
    print("=" * 60)
    print("  CRYPTO MONITOR — HEALTH CHECK")
    print("=" * 60)

    required_results: list[bool] = []

    # ── RSS Exchange feedy ────────────────────────────────────────
    print("\n📡 RSS Exchange Feedy:")
    for name, url in EXCHANGE_FEEDS.items():
        ok = check_feed(name, url)
        required_results.append(ok)

    # ── API zdroje ───────────────────────────────────────────────
    print("\n🔑 API Zdroje:")
    required_results.append(check_cryptopanic())
    check_coinmarketcap()   # volitelné, neblokuje workflow

    # ── Telegram ─────────────────────────────────────────────────
    print("\n📬 Telegram:")
    required_results.append(check_telegram())

    # ── Výsledek ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    failed = sum(1 for r in required_results if r is False)
    total  = len(required_results)
    ok     = total - failed

    if failed:
        print(f"  ❌ SELHALO {failed}/{total} zdrojů – zkontroluj výstup výše")
        print("=" * 60)
        sys.exit(1)
    else:
        print(f"  ✅ Všechny zdroje fungují ({ok}/{total})")
        print("=" * 60)


if __name__ == "__main__":
    main()
