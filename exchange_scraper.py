"""
exchange_scraper.py
Web scraping + JSON API alternativa k RSS feedům.

Strategie pro každou burzu:
  Binance      → interní JSON API (catalogId=161 delistingy, catalogId=48 obecná)
  Bybit        → JSON API (api2.bybit.com)
  Kraken       → Zendesk JSON API (support.kraken.com)
  Coinbase     → HTML scraping blogu
  OKX          → HTML scraping announcement sekce
  KuCoin       → HTML scraping announcement centra
  Gate.io      → HTML scraping announcement sekce
  HTX          → HTML scraping support centra
  Crypto.com   → HTML scraping announcement stránky
"""

import hashlib
import logging
import re
import time

import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

TIMEOUT = 15

_BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

_JSON_HEADERS = {
    **_BROWSER_HEADERS,
    "Accept": "application/json, */*;q=0.8",
}

_HTML_HEADERS = {
    **_BROWSER_HEADERS,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _get(url: str, *, use_json: bool = False, params: dict = None) -> requests.Response | None:
    headers = _JSON_HEADERS if use_json else _HTML_HEADERS
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as e:
        log.warning("Scrape GET failed (%s): %s", url, e)
        return None


def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def _dedup(items: list[dict]) -> list[dict]:
    """Odstraní duplikáty podle URL."""
    seen = set()
    out = []
    for item in items:
        key = item.get("url") or item.get("title", "")
        if key and key not in seen:
            seen.add(key)
            out.append(item)
    return out


# ─── BINANCE ──────────────────────────────────────────────────────────────────

def scrape_binance() -> list[dict]:
    """
    Binance interní JSON API.
    catalogId=161 = delistingy, catalogId=48 = obecná oznámení.
    """
    results = []
    for catalog_id, source_name in [(161, "BinanceDelisting"), (48, "Binance")]:
        resp = _get(
            "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
            use_json=True,
            params={"type": 1, "pageNo": 1, "pageSize": 20, "catalogId": catalog_id},
        )
        if not resp:
            continue
        try:
            data = resp.json()
            # Struktura: data.catalogs[].articles[] nebo rovnou data.articles[]
            catalogs = data.get("data", {}).get("catalogs", [])
            articles = []
            if catalogs:
                for cat in catalogs:
                    articles.extend(cat.get("articles", []))
            else:
                articles = data.get("data", {}).get("articles", [])
            for a in articles:
                title = a.get("title", "").strip()
                code = a.get("code", "") or str(a.get("id", ""))
                url = f"https://www.binance.com/en/support/announcement/{code}" if code else ""
                if title:
                    results.append({"title": title, "url": url, "source": source_name})
        except Exception as e:
            log.error("Binance JSON parse error (catalogId=%d): %s", catalog_id, e)
        time.sleep(0.5)
    return results


# ─── BYBIT ────────────────────────────────────────────────────────────────────

def scrape_bybit() -> list[dict]:
    """Bybit JSON API — announcement centrum."""
    resp = _get(
        "https://api2.bybit.com/v2/announcements/index",
        use_json=True,
        params={"locale": "en-US", "page": 1, "limit": 20},
    )
    if not resp:
        return []
    try:
        items = resp.json().get("result", {}).get("list", [])
        results = []
        for item in items:
            title = item.get("title", "").strip()
            url = item.get("url", "") or f"https://announcements.bybit.com/en-US/{item.get('id', '')}"
            if title:
                results.append({"title": title, "url": url, "source": "Bybit"})
        return results
    except Exception as e:
        log.error("Bybit JSON parse error: %s", e)
        return []


# ─── KRAKEN ───────────────────────────────────────────────────────────────────

def scrape_kraken() -> list[dict]:
    """
    Zendesk JSON API — Kraken Support.
    Sekce 200187503 = Announcements (delistingy, migrace).
    """
    # Zkusíme nejprve přímo sekci Announcements
    resp = _get(
        "https://support.kraken.com/api/v2/help_center/en-us/sections/200187503/articles.json",
        use_json=True,
        params={"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
    )
    if not resp:
        # Fallback: hledat přes label
        resp = _get(
            "https://support.kraken.com/api/v2/help_center/en-us/articles.json",
            use_json=True,
            params={"label_names": "announcements", "sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        )
    if not resp:
        return []
    try:
        articles = resp.json().get("articles", [])
        return [
            {"title": a.get("title", "").strip(), "url": a.get("html_url", ""), "source": "KrakenSupport"}
            for a in articles if a.get("title")
        ]
    except Exception as e:
        log.error("Kraken Zendesk parse error: %s", e)
        return []


# ─── COINBASE ─────────────────────────────────────────────────────────────────

def scrape_coinbase() -> list[dict]:
    """HTML scraping — Coinbase blog, sekce s asset news."""
    for url in [
        "https://www.coinbase.com/blog/landing/assets",
        "https://www.coinbase.com/blog",
    ]:
        resp = _get(url)
        if resp:
            break
    else:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/blog/")):
        # Hledáme nadpis uvnitř odkazu
        title_el = a.find(["h1", "h2", "h3", "h4"])
        title = title_el.get_text(strip=True) if title_el else a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://www.coinbase.com{href}"
        results.append({"title": title, "url": full_url, "source": "Coinbase"})
    return _dedup(results)[:20]


# ─── OKX ─────────────────────────────────────────────────────────────────────

def scrape_okx() -> list[dict]:
    """HTML scraping — OKX Help Center, sekce delistings."""
    for url in [
        "https://www.okx.com/help/section/announcements-delistings",
        "https://www.okx.com/help/section/latest-announcements",
    ]:
        resp = _get(url)
        if resp:
            break
    else:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/help/")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://www.okx.com{href}"
        results.append({"title": title, "url": full_url, "source": "OKX"})
    return _dedup(results)[:20]


# ─── KUCOIN ───────────────────────────────────────────────────────────────────

def scrape_kucoin() -> list[dict]:
    """HTML scraping — KuCoin Announcement Center (delistingy)."""
    for url in [
        "https://www.kucoin.com/news/categories/soft-delisting",
        "https://www.kucoin.com/announcement",
    ]:
        resp = _get(url)
        if resp:
            break
    else:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/news/|/announcement")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://www.kucoin.com{href}"
        results.append({"title": title, "url": full_url, "source": "KuCoin"})
    return _dedup(results)[:20]


# ─── GATE.IO ──────────────────────────────────────────────────────────────────

def scrape_gate() -> list[dict]:
    """HTML scraping — Gate.io Announcements (delisted sekce)."""
    for url in [
        "https://www.gate.io/en/article/delisted",
        "https://www.gate.io/en/article/announcements",
    ]:
        resp = _get(url)
        if resp:
            break
    else:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/en/article/")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://www.gate.io{href}"
        results.append({"title": title, "url": full_url, "source": "Gate"})
    return _dedup(results)[:20]


# ─── HTX (HUOBI) ──────────────────────────────────────────────────────────────

def scrape_htx() -> list[dict]:
    """HTML scraping — HTX Support Center, sekce oznámení."""
    resp = _get("https://www.htx.com/support/en-us/list/360000043694")
    if not resp:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/support/en-us/")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://www.htx.com{href}"
        results.append({"title": title, "url": full_url, "source": "HTX"})
    return _dedup(results)[:20]


# ─── CRYPTO.COM ───────────────────────────────────────────────────────────────

def scrape_cryptocom() -> list[dict]:
    """HTML scraping — Crypto.com Exchange announcement stránka."""
    for url in [
        "https://crypto.com/exchange/announcements/list",
        "https://crypto.com/en/news",
    ]:
        resp = _get(url)
        if resp:
            break
    else:
        return []

    soup = _soup(resp.text)
    results = []
    for a in soup.find_all("a", href=re.compile(r"/exchange/announcements/|/en/news/")):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        if not title or len(title) < 10:
            continue
        full_url = href if href.startswith("http") else f"https://crypto.com{href}"
        results.append({"title": title, "url": full_url, "source": "CryptoCom"})
    return _dedup(results)[:20]


# ─── HLAVNÍ FUNKCE ────────────────────────────────────────────────────────────

_SCRAPERS = [
    scrape_binance,
    scrape_bybit,
    scrape_kraken,
    scrape_coinbase,
    scrape_okx,
    scrape_kucoin,
    scrape_gate,
    scrape_htx,
    scrape_cryptocom,
]


def fetch_all_scrapers() -> list[dict]:
    """
    Spustí všechny scrapery a vrátí surový seznam článků.
    Každý item: {"title": str, "url": str, "source": str}
    Chyby jednoho scraperu nezastaví ostatní.
    """
    all_items = []
    for scraper in _SCRAPERS:
        name = scraper.__name__
        try:
            items = scraper()
            log.info("Scraper %-25s → %d článků", name, len(items))
            all_items.extend(items)
        except Exception as e:
            log.error("Scraper %s selhal neočekávaně: %s", name, e)
        time.sleep(0.3)
    return all_items
