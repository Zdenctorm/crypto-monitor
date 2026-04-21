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
  Coinbase     → Zendesk JSON API (help.coinbase.com) + Medium blog RSS
  Telegram     → web preview t.me/s/{channel} pro burzy bez API
                 (Bybit, OKX, Gate, CryptoCom, HTX, Coinbase)
"""

import json
import logging
import re
import time
import xml.etree.ElementTree as ET

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
    """Bybit v5 REST API — announcement centrum."""
    for base_url in [
        "https://api.bybit.com/v5/announcements/index",
        "https://api2.bybit.com/v2/announcements/index",
    ]:
        resp = _get(base_url, use_json=True, params={"locale": "en-US", "page": 1, "limit": 20})
        if not resp:
            continue
        try:
            data = resp.json()
            # v5 API používá retCode=0 pro úspěch
            if "retCode" in data and data["retCode"] != 0:
                continue
            items = data.get("result", {}).get("list", [])
            results = []
            for item in items:
                title = item.get("title", "").strip()
                url = item.get("url", "") or f"https://announcements.bybit.com/en-US/?id={item.get('id', '')}"
                if title:
                    results.append({"title": title, "url": url, "source": "Bybit"})
            if results:
                return results
        except Exception as e:
            log.error("Bybit JSON parse error (%s): %s", base_url, e)
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
    HTX support centrum běží na Zendesk.
    HTX (dříve Huobi) přejmenoval Zendesk z huobiglobal na htxglobal.
    """
    for url, params in [
        # Nový HTX Zendesk (po rebrandingu z Huobi → HTX v 2023)
        (
            "https://htxglobal.zendesk.com/api/v2/help_center/en-us/articles.json",
            {"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
        (
            "https://htxglobal.zendesk.com/api/v2/help_center/en-us/sections/360000070201/articles.json",
            {"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
        # Starý Huobi Zendesk jako fallback
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
            soup = _soup(resp.text)
            # Najdeme SSR data script tag
            script = soup.find("script", {"data-id": "__app_data_for_ssr__"})
            if not script or not script.string:
                log.warning("OKX: SSR script tag nenalezen pro sekci %s", section_slug)
                continue
            data = json.loads(script.string)
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
    Pokus 1: api.gate.io/articlelist; Pokus 2: web API fallbacky;
    Pokus 3: Medium RSS (gate-io blog, není za Cloudflare).
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
                    continue
            except Exception as e:
                log.warning("Gate.io API parse error (category=%s): %s", category, e)

    if results:
        return _dedup(results)[:40]

    # Pokus 2: Gate.io web API (alternativní endpointy)
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

    # Pokus 3: Medium RSS pro gate-io blog (není za Gate.io Cloudflare)
    for medium_url in [
        "https://medium.com/feed/gate-io",
        "https://gateio.medium.com/feed",
    ]:
        resp = _get(medium_url)
        if not resp:
            continue
        try:
            root = ET.fromstring(resp.text)
            items = root.findall(".//item")
            for item in items[:20]:
                title_el = item.find("title")
                link_el = item.find("link")
                title = title_el.text.strip() if title_el is not None and title_el.text else ""
                url = link_el.text.strip() if link_el is not None and link_el.text else ""
                if title and len(title) >= 10:
                    results.append({"title": title, "url": url, "source": "Gate"})
            if results:
                log.info("Gate.io Medium RSS (%s) → %d článků", medium_url, len(results))
                return results
        except ET.ParseError as e:
            log.warning("Gate.io Medium RSS parse error (%s): %s", medium_url, e)
        except Exception as e:
            log.warning("Gate.io Medium RSS error (%s): %s", medium_url, e)

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


def scrape_coinbase_help() -> list[dict]:
    """
    Coinbase Help Center — Zendesk JSON API.
    help.coinbase.com běží na Zendesk; API vrací nejnovější articles.
    Pokrývá delistingy a migrace které nejsou na blogu.
    """
    for url, params in [
        # Obecné nejnovější články — zachytí announcements
        (
            "https://help.coinbase.com/api/v2/help_center/en-us/articles.json",
            {"sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
        # Fallback: articles s labelem announcements
        (
            "https://help.coinbase.com/api/v2/help_center/en-us/articles.json",
            {"label_names": "announcements", "sort_by": "created_at", "sort_order": "desc", "per_page": 20},
        ),
    ]:
        resp = _get(url, use_json=True, params=params)
        if not resp:
            continue
        try:
            articles = resp.json().get("articles", [])
            if not articles:
                continue
            return [
                {"title": a.get("title", "").strip(), "url": a.get("html_url", ""), "source": "CoinbaseHelp"}
                for a in articles if a.get("title")
            ]
        except Exception as e:
            log.error("Coinbase Help Zendesk parse error: %s", e)

    return []


# ─── TELEGRAM KANÁLY ──────────────────────────────────────────────────────────

def _scrape_telegram_channel(channel: str, source: str) -> list[dict]:
    """
    Scrapuje veřejný Telegram kanál přes web preview (t.me/s/{channel}).
    Nevyžaduje autentizaci — funguje pro libovolný veřejný kanál.
    Vrátí posledních max. 20 zpráv jako list[dict].
    """
    url = f"https://t.me/s/{channel}"
    resp = _get(url)
    if not resp:
        return []

    # HTTP 200 ale přesměrování na login = kanál je privátní nebo neexistuje
    if "tgme_page_photo" not in resp.text and "tgme_widget_message" not in resp.text:
        log.warning("Telegram: kanál %s nenalezen nebo je privátní", channel)
        return []

    try:
        soup = _soup(resp.text)
        results = []
        for msg in soup.select(".tgme_widget_message"):
            text_el = msg.select_one(".tgme_widget_message_text")
            link_el = msg.select_one("a.tgme_widget_message_date")
            if not text_el:
                continue
            title = text_el.get_text(" ", strip=True)
            # Zkrátíme na 300 znaků — zbytek je kontext který nepotřebujeme
            title = title[:300].strip()
            msg_url = link_el["href"] if link_el and link_el.get("href") else f"https://t.me/{channel}"
            if title and len(title) >= 10:
                results.append({"title": title, "url": msg_url, "source": source})
        # Telegram vrací zprávy od nejstarší; chceme nejnovější
        return list(reversed(results))[:20]
    except Exception as e:
        log.error("Telegram scrape error (%s): %s", channel, e)
        return []


def scrape_telegram_bybit() -> list[dict]:
    """Bybit officiální announcement kanál na Telegramu."""
    return _scrape_telegram_channel("BybitAnnouncements", "Bybit")


def scrape_telegram_okx() -> list[dict]:
    """OKX officiální announcement kanál na Telegramu."""
    return _scrape_telegram_channel("OKXAnnouncements", "OKX")


def scrape_telegram_gate() -> list[dict]:
    """Gate.io officiální announcement kanál na Telegramu."""
    for channel in ["GateioAnnouncements", "gate_io", "GateAnnouncements"]:
        result = _scrape_telegram_channel(channel, "Gate")
        if result:
            return result
    return []


def scrape_telegram_cryptocom() -> list[dict]:
    """Crypto.com officiální kanál na Telegramu."""
    return _scrape_telegram_channel("CryptoComChannel", "CryptoCom")


def scrape_telegram_htx() -> list[dict]:
    """HTX (přejmenovaný z Huobi) officiální kanál na Telegramu."""
    for channel in ["HTXglobal", "HTX_Global", "HTX_Official"]:
        result = _scrape_telegram_channel(channel, "HTX")
        if result:
            return result
    return []


# ─── HLAVNÍ FUNKCE ────────────────────────────────────────────────────────────

_SCRAPERS = [
    # JSON API scrapery (primární, nejspolehlivější)
    scrape_binance,
    scrape_bybit,
    scrape_kraken,
    scrape_kucoin,
    scrape_htx,
    scrape_cryptocom,
    scrape_okx,
    scrape_gate,
    # Coinbase — blog RSS + help center Zendesk API
    scrape_coinbase,
    scrape_coinbase_help,
    # Telegram kanály (záloha pro burzy kde API selhává nebo chybí)
    scrape_telegram_bybit,
    scrape_telegram_okx,
    scrape_telegram_gate,
    scrape_telegram_cryptocom,
    scrape_telegram_htx,
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
