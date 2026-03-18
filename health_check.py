#!/usr/bin/env python3
"""
health_check.py
Ověří dostupnost všech zdrojů (RSS feedy, CryptoPanic API, CoinMarketCap, Telegram).
Spouštěj ručně nebo automaticky před monitorem v GitHub Actions.

Výstup:
  ✅ zdroj OK
  ❌ zdroj selhal     → workflow skončí s exit code 1  (povinný zdroj)
  ⚠️  zdroj selhal    → jen varování, workflow pokračuje (volitelný zdroj)
  ⚠️  zdroj přeskočen → chybí API key (volitelné)

Volitelné feedy (OPTIONAL_FEEDS) jsou exchange support/announcement centra,
která mohou občas omezit přístup (rate-limit, Cloudflare). Jejich selhání
nezablokuje monitor; hlavní feed dané burzy pokrývá stejná oznámení.
"""

import os
import sys
import requests
import feedparser

# Přímý import aby health_check fungoval i bez nastavených env vars
from config import EXCHANGE_FEEDS

# Feedy, které jsou "volitelné" — jejich selhání nevyhodí exit(1).
# BinanceDelisting je záloha k hlavnímu Binance feedu; ostatní jsou povinné.
OPTIONAL_FEEDS = {
    "BinanceDelisting",   # kategorie navId=161 — záloha k hlavnímu Binance feedu
}

CRYPTOPANIC_API_KEY   = os.environ.get("CRYPTOPANIC_API_KEY", "")
TELEGRAM_BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID      = os.environ.get("TELEGRAM_CHAT_ID", "")
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")


def check_feed(name: str, url: str) -> bool:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0 (compatible; crypto-monitor/1.0; +https://github.com)"})
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)
        entry_count = len(feed.entries)
        if feed.bozo and entry_count == 0:
            print(f"  ❌ {name}: prázdný nebo chybný feed ({feed.bozo_exception})")
            return False
        if entry_count == 0:
            # Feed vrátí HTTP 200 + validní XML ale 0 položek → možný Cloudflare soft-block
            print(f"  ⚠️  {name}: HTTP 200 ale 0 položek – možný Cloudflare soft-block! ({url})")
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


def check_bybit_api() -> bool:
    """Ověří Bybit V5 Announcements API (náhrada za RSS, které vrací 403)."""
    try:
        resp = requests.get(
            "https://api.bybit.com/v5/announcements/index",
            params={"locale": "en-US", "limit": 1},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        count = len(data.get("result", {}).get("list", []))
        total = data.get("result", {}).get("total", "?")
        print(f"  ✅ Bybit API: OK ({total} oznámení celkem)")
        return True
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ Bybit API: HTTP {e.response.status_code}")
        return False
    except Exception as e:
        print(f"  ❌ Bybit API: {e}")
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


def send_telegram_alert(failed_feeds: list[str]):
    """Pošle Telegram zprávu pokud jsou nefunkční feedy."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    lines = ["⚠️ <b>Health Check – nefunkční zdroje</b>"]
    for name in failed_feeds:
        lines.append(f"  ❌ {name}")
    lines.append("\nMonitor běží, ale tato data dnes chybí. Zkontroluj GitHub Actions log.")
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

    failed_names: list[str] = []
    required_results: list[bool] = []

    # ── RSS Exchange feedy ────────────────────────────────────────
    print("\n📡 RSS Exchange Feedy (povinné):")
    for name, url in EXCHANGE_FEEDS.items():
        if name in OPTIONAL_FEEDS:
            continue
        ok = check_feed(name, url)
        required_results.append(ok)
        if not ok:
            failed_names.append(name)

    print("\n📡 RSS Exchange Feedy (volitelné — selhání nevyhodí chybu):")
    for name, url in EXCHANGE_FEEDS.items():
        if name not in OPTIONAL_FEEDS:
            continue
        ok = check_feed(name, url)
        if not ok:
            print(f"     ↳ {name} selhal – volitelný feed, monitor pokračuje")
            failed_names.append(f"{name} (volitelný)")

    # ── API zdroje ───────────────────────────────────────────────
    print("\n🔑 API Zdroje:")
    cp_ok = check_cryptopanic()
    required_results.append(cp_ok)
    if not cp_ok:
        failed_names.append("CryptoPanic API")

    bybit_ok = check_bybit_api()
    required_results.append(bybit_ok)
    if not bybit_ok:
        failed_names.append("Bybit API")

    check_coinmarketcap()   # volitelné, neblokuje workflow

    # ── Telegram ─────────────────────────────────────────────────
    print("\n📬 Telegram:")
    tg_ok = check_telegram()
    required_results.append(tg_ok)

    # ── Výsledek ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    failed = sum(1 for r in required_results if r is False)
    total  = len(required_results)
    ok_count = total - failed

    if failed:
        print(f"  ❌ SELHALO {failed}/{total} zdrojů – zkontroluj výstup výše")
        print("=" * 60)
        # Pošli Telegram alert o nefunkčních feedech (pokud Telegram funguje)
        if tg_ok and failed_names:
            send_telegram_alert(failed_names)
        sys.exit(1)
    else:
        print(f"  ✅ Všechny zdroje fungují ({ok_count}/{total})")
        print("=" * 60)


if __name__ == "__main__":
    main()
