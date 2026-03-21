"""
exchange_scraper.py
Web scraping + JSON API alternativa k RSS feedům.

Strategie pro každou burzu:
  Binance      → interní JSON API (catalogId=161 delistingy, catalogId=48 obecná)
  Bybit        → JSON API (api2.bybit.com)
  Kraken       → Zendesk JSON API (support.kraken.com)
  KuCoin       → oficiální v3 REST API (api.kucoin.com/api/v3/announcements)
  HTX          → Zendesk JSON API (huobiglobal.zendesk.com)
  Crypto.com   → veřejné POST API (api.crypto.com/v1/public/get-announcements)
  OKX          → SSR JSON embed v HTML stránce (script[data-id=__app_data_for_ssr__])
  Gate.io      → interní JSON API (api.gate.io/articlelist)
  Coinbase     → Medium RSS feed (blog.coinbase.com/feed) + fallback HTML
"""

import json
import logging
import re
import time
import xml.etree.ElementTree as ET

import requests

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
        log.warning("GET failed (%s): %s", url, e)
        return None


def _post(url: str, body: dict) -> requests.Response | None:
    try:
        resp = requests.post(url, json=body, headers=_JSON_HEADERS, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp
    except Exception as e:
        log.warning("POST failed (%s): %s", url, e)
        return None



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
    resp = _get(
        "https://support.kraken.com/api/v2/help_center/en-us/sections/200187503/articles.json",
        use_json=True,
        params={"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
    )
    if not resp:
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


# ─── KUCOIN ───────────────────────────────────────────────────────────────────

def scrape_kucoin() -> list[dict]:
    """
    KuCoin oficiální v3 REST API.
    Dokumentace: https://www.kucoin.com/docs-new/rest/spot-trading/market-data/get-announcements
    annType=delistings zachytí přímo delistingy; latest-announcements zachytí vše nové.
    """
    results = []
    for ann_type in ["delistings", "latest-announcements"]:
        resp = _get(
            "https://api.kucoin.com/api/v3/announcements",
            use_json=True,
            params={"annType": ann_type, "lang": "en_US", "currentPage": 1, "pageSize": 20},
        )
        if not resp:
            continue
        try:
            data = resp.json()
            if data.get("code") != "200000":
                log.warning("KuCoin API vrátil chybu (annType=%s): %s", ann_type, data.get("msg"))
                continue
            items = data.get("data", {}).get("items", [])
            for item in items:
                title = item.get("annTitle", "").strip()
                url = item.get("annUrl", "")
                if title:
                    results.append({"title": title, "url": url, "source": "KuCoin"})
        except Exception as e:
            log.error("KuCoin JSON parse error (annType=%s): %s", ann_type, e)
        time.sleep(0.3)
    return _dedup(results)


# ─── HTX (HUOBI) ──────────────────────────────────────────────────────────────

def scrape_htx() -> list[dict]:
    """
    HTX support centrum běží na Zendesk (huobiglobal.zendesk.com).
    Stahujeme nejnovější články ze sekce oznámení.
    """
    # Zkusíme nejprve specifickou sekci oznámení (section_id z HTX URL vzorů)
    for url, params in [
        (
            "https://huobiglobal.zendesk.com/api/v2/help_center/en-us/sections/360000070201/articles.json",
            {"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
        (
            "https://huobiglobal.zendesk.com/api/v2/help_center/en-us/articles.json",
            {"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
    ]:
        resp = _get(url, use_json=True, params=params)
        if resp:
            break
    else:
        return []

    try:
        articles = resp.json().get("articles", [])
        return [
            {"title": a.get("title", "").strip(), "url": a.get("html_url", ""), "source": "HTX"}
            for a in articles if a.get("title")
        ]
    except Exception as e:
        log.error("HTX Zendesk parse error: %s", e)
        return []


# ─── CRYPTO.COM ───────────────────────────────────────────────────────────────

def scrape_cryptocom() -> list[dict]:
    """
    Crypto.com Exchange veřejné API — announcements endpoint.
    Dokumentace: https://exchange-docs.crypto.com/exchange/v1/rest-ws/index.html
    """
    body = {
        "id": 1,
        "method": "public/get-announcements",
        "params": {},
        "nonce": int(time.time() * 1000),
    }
    resp = _post("https://api.crypto.com/v1/public/get-announcements", body)
    if not resp:
        return []
    try:
        data = resp.json()
        if data.get("code") != 0:
            log.warning("Crypto.com API chyba: %s", data.get("message"))
            return []
        items = data.get("result", {}).get("data", [])
        results = []
        for item in items:
            title = item.get("title", "").strip()
            # API nevrací přímé URL; sestavíme odkaz na announcements stránku
            ann_id = item.get("id", "")
            url = f"https://crypto.com/exchange/announcements/{ann_id}" if ann_id else "https://crypto.com/exchange/announcements"
            if title:
                results.append({"title": title, "url": url, "source": "CryptoCom"})
        return results
    except Exception as e:
        log.error("Crypto.com JSON parse error: %s", e)
        return []


# ─── OKX ─────────────────────────────────────────────────────────────────────

def scrape_okx() -> list[dict]:
    """
    OKX help center používá Next.js SSR — data jsou vložena přímo do HTML
    v tagu <script data-id="__app_data_for_ssr__"> jako JSON objekt.
    Funguje s běžným HTTP requestem (není potřeba headless browser).
    """
    results = []
    for section_slug, source_label in [
        ("announcements-delistings", "OKXDelisting"),
        ("latest-announcements", "OKX"),
    ]:
        url = f"https://www.okx.com/help/section/{section_slug}"
        resp = _get(url)
        if not resp:
            continue
        try:
            # Regex extrakce JSON z <script data-id="__app_data_for_ssr__">…</script>
            m = re.search(
                r'<script[^>]+data-id=["\']__app_data_for_ssr__["\'][^>]*>(.*?)</script>',
                resp.text,
                re.DOTALL,
            )
            if not m:
                log.warning("OKX: SSR script tag nenalezen pro sekci %s", section_slug)
                continue
            data = json.loads(m.group(1))
            # Navigujeme JSON strukturou
            article_list = (
                data.get("appContext", {})
                    .get("initialProps", {})
                    .get("sectionData", {})
                    .get("articleList", {})
            )
            items = article_list.get("items", [])
            if not items:
                # Alternativní cesta v JSON struktuře
                items = (
                    data.get("initialProps", {})
                        .get("sectionData", {})
                        .get("articleList", {})
                        .get("items", [])
                )
            for item in items:
                title = item.get("title", "").strip()
                slug = item.get("slug", "") or str(item.get("id", ""))
                article_url = f"https://www.okx.com/help/{slug}" if slug else ""
                if title:
                    results.append({"title": title, "url": article_url, "source": source_label})
        except json.JSONDecodeError as e:
            log.error("OKX SSR JSON parse error (%s): %s", section_slug, e)
        except Exception as e:
            log.error("OKX scrape error (%s): %s", section_slug, e)
        time.sleep(0.5)
    return _dedup(results)


# ─── GATE.IO ──────────────────────────────────────────────────────────────────

def scrape_gate() -> list[dict]:
    """
    Gate.io interní JSON API pro články/oznámení.
    Primárně zkusíme api.gate.io/articlelist; fallback na web API.
    """
    results = []

    # Pokus 1: api.gate.io/articlelist s filtrováním kategorie
    for category, source_label in [("Delisted", "GateDelisted"), ("Announcement", "Gate")]:
        resp = _get(
            "https://api.gate.io/articlelist",
            use_json=True,
            params={"type": category, "page": 1, "size": 20},
        )
        if resp:
            try:
                data = resp.json()
                # Zkusíme různé struktury odpovědi
                items = []
                if isinstance(data, list):
                    items = data
                elif isinstance(data, dict):
                    items = data.get("data", data.get("list", data.get("articles", [])))
                for item in items:
                    title = item.get("title", "").strip()
                    item_id = item.get("id", "")
                    url = item.get("url", "") or (f"https://www.gate.io/announcements/article/{item_id}" if item_id else "")
                    if title:
                        results.append({"title": title, "url": url, "source": source_label})
                if results:
                    continue  # Pokračujeme s dalšími kategoriemi
            except Exception as e:
                log.warning("Gate.io API parse error (category=%s): %s", category, e)

    if results:
        return _dedup(results)[:40]

    # Pokus 2: Gate.io web API (alternativní endpoint)
    for api_url in [
        "https://www.gate.io/apiw/article/list",
        "https://www.gate.io/api/web/article/list",
    ]:
        resp = _get(api_url, use_json=True, params={"page": 1, "pageSize": 20})
        if resp:
            try:
                data = resp.json()
                items = data.get("data", data.get("list", []))
                if isinstance(items, list) and items:
                    for item in items:
                        title = item.get("title", "").strip()
                        item_id = item.get("id", "")
                        url = item.get("url", "") or (f"https://www.gate.io/announcements/article/{item_id}" if item_id else "")
                        if title:
                            results.append({"title": title, "url": url, "source": "Gate"})
                    return _dedup(results)[:20]
            except Exception as e:
                log.warning("Gate.io web API parse error (%s): %s", api_url, e)

    return results


# ─── COINBASE ─────────────────────────────────────────────────────────────────

def scrape_coinbase() -> list[dict]:
    """
    Coinbase blog — Medium RSS feed (blog.coinbase.com/feed).
    Coinbase nemá veřejné JSON API pro blog články; Medium RSS je nejspolehlivější zdroj.
    Fallback: www.coinbase.com/blog/rss
    """
    for rss_url in [
        "https://blog.coinbase.com/feed",
        "https://www.coinbase.com/blog/landing/rss",
    ]:
        resp = _get(rss_url)
        if not resp:
            continue
        try:
            root = ET.fromstring(resp.text)
            # RSS 2.0 struktura: rss > channel > item
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            items = root.findall(".//item")
            results = []
            for item in items[:20]:
                title_el = item.find("title")
                link_el = item.find("link")
                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                url = link_el.text.strip() if link_el is not None and link_el.text else ""
                if title and len(title) >= 10:
                    results.append({"title": title, "url": url, "source": "Coinbase"})
            if results:
                log.info("Coinbase RSS (%s) → %d článků", rss_url, len(results))
                return results
        except ET.ParseError as e:
            log.warning("Coinbase RSS parse error (%s): %s", rss_url, e)
        except Exception as e:
            log.warning("Coinbase RSS error (%s): %s", rss_url, e)

    return []


# ─── HLAVNÍ FUNKCE ────────────────────────────────────────────────────────────

_SCRAPERS = [
    scrape_binance,
    scrape_bybit,
    scrape_kraken,
    scrape_kucoin,
    scrape_htx,
    scrape_cryptocom,
    scrape_okx,
    scrape_gate,
    scrape_coinbase,
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
