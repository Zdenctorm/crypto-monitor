#!/usr/bin/env python3
"""
verify_scrapers.py
Otestuje všechny scrapery a vypíše co stáhly.
Spusť: python3 verify_scrapers.py

Výstup pro každý scraper:
  ✅ <jméno>  → N článků
       1. Titulek | URL
       2. ...
  ❌ <jméno>  → 0 článků (nebo chyba)
"""

import logging
import sys

# Zobraz WARNING+ logy scraperů
logging.basicConfig(level=logging.WARNING, format="%(levelname)s [%(name)s] %(message)s")

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
)

SCRAPERS = [
    ("Binance (JSON API)",         scrape_binance),
    ("Bybit (JSON API)",           scrape_bybit),
    ("Kraken (Zendesk API)",       scrape_kraken),
    ("KuCoin (v3 REST API)",       scrape_kucoin),
    ("HTX (Zendesk API)",          scrape_htx),
    ("Crypto.com (POST API)",      scrape_cryptocom),
    ("OKX (SSR JSON)",             scrape_okx),
    ("Gate.io (JSON API)",         scrape_gate),
    ("Coinbase (RSS)",             scrape_coinbase),
]

GREEN = "\033[92m"
RED   = "\033[91m"
RESET = "\033[0m"
BOLD  = "\033[1m"

total_ok = 0
total_fail = 0

print(f"\n{BOLD}=== Verifikace scraperů ==={RESET}\n")

for label, fn in SCRAPERS:
    print(f"  Testuji {label}...", end=" ", flush=True)
    try:
        items = fn()
    except Exception as e:
        print(f"\r  {RED}❌ {label:<30}{RESET} → chyba: {e}")
        total_fail += 1
        continue

    if items:
        print(f"\r  {GREEN}✅ {label:<30}{RESET} → {len(items)} článků")
        for i, item in enumerate(items[:5], 1):
            title = item.get("title", "")[:80]
            url   = item.get("url", "")[:60]
            print(f"       {i}. {title}")
            if url:
                print(f"          {url}")
        if len(items) > 5:
            print(f"       ... a dalších {len(items) - 5}")
        total_ok += 1
    else:
        print(f"\r  {RED}❌ {label:<30}{RESET} → 0 článků")
        total_fail += 1

    print()

print(f"{BOLD}=== Výsledek ==={RESET}")
print(f"  {GREEN}✅ Funkční:{RESET}  {total_ok} / {len(SCRAPERS)}")
print(f"  {RED}❌ Nefunkční:{RESET} {total_fail} / {len(SCRAPERS)}\n")

sys.exit(0 if total_fail == 0 else 1)
