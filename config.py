# ── KONFIGURACE ──────────────────────────────────────────────────────────────

import os

CRYPTOPANIC_API_KEY  = os.environ.get("CRYPTOPANIC_API_KEY", "")
TELEGRAM_BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID     = os.environ.get("TELEGRAM_CHAT_ID", "")

LINEAR_API_KEY       = os.environ.get("LINEAR_API_KEY", "")
# Ops team + zdenal (Zdeněk Mareček) — pevné hodnoty, nemění se
LINEAR_TEAM_ID       = "33cf2dd4-689b-4707-88b2-5f4263846bea"
LINEAR_ASSIGNEE_ID   = "2b21c6af-3ee9-4519-bb70-6e3341d891c9"

# Tokeny ze seznamu (Kraken Europe listing)
TOKENS = [
    "1INCH","AAVE","ACA","ACH","ACT","ACX","ADA","ADX","AERO","AEVO","AGLD","AI16Z",
    "AIOZ","AIR","AIXBT","AKT","ALCX","ALGO","ALICE","ALPHA","ALT","ANKR","ANLOG",
    "ANON","APE","APENFT","API3","APT","APU","ARB","ARKM","ARPA","ASTR","ATH",
    "ATLAS","ATOM","AUCTION","AUDIO","AVAAI","AVAX","AXS","B3","BADGER","BAL",
    "BANANAS31","BAND","BAT","BCH","BEAM","BICO","BIGTIME","BIO","BIT","BLUR",
    "BLZ","BMT","BNB","BNC","BNT","BOBA","BOND","BONK","BSX","BTC","BTT","C98",
    "CAKE","CELR","CFG","CHEEMS","CHEX","CHR","CHZ","CLOUD","CLV","COMP","COOKIE",
    "COTI","COW","CPOOL","CQT","CRO","CRV","CTSI","CVC","CVX","CXT","CYBER","DAI",
    "DBR","DEEP","DENT","DMC","DOGS","DOT","DRIFT","DRV","DYDX","EGLD","EIGEN",
    "ELIZAOS","ELX","ENA","ENJ","ENS","EOS","ETC","ETH","ETHFI","ETHW","EUL",
    "EURC","EURQ","EURR","EWT","FARM","FARTCOIN","FET","FHE","FIDA","FIL","FIS",
    "FLOKI","FLOW","FLR","FLUX","FORTH","FWOG","FXS","G","GAL","GALA","GARI",
    "GFI","GHST","GIGA","GLMR","GMT","GMX","GNO","GOAT","GOMINING","GRASS",
    "GRIFFAIN","GRT","GST","GTC","GUN","H","HDX","HFT","HNT","HONEY","HPOS10I",
    "ICP","ICX","IDEX","IMX","INJ","INTR","JAILSTOOL","JASMY","JTO","JUNO","JUP",
    "KAITO","KAR","KAS","KAVA","KEEP","KERNEL","KET","KEY","KILT","KIN","KINT",
    "KMNO","KNC","KOBAN","KP3R","KSM","KTA","L3","LAYER","LCX","LDO","LINK",
    "LMWR","LOCKIN","LPT","LQTY","LRC","LSETH","LSK","LTC","LUNA","M","MANA",
    "MANTRA","MASK","ME","MELANIA","MEME","MERL","MEW","MICHI","MINA","MIR",
    "MIRROR","MKR","MLN","MNGO","MNT","MOG","MOODENG","MORPHO","MOVE","MOVR",
    "MSOL","MUBARAK","MULTI","MV","MXC","NANO","NEAR","NEIRO","NMR","NOBODY",
    "NODL","NOS","NOT","NPC","OCEAN","ODOS","OGN","OM","OMG","OMNI","ONDO",
    "OOB","OP","OPEN","ORCA","OXT","OXY","PAXG","PDA","PENDLE","PENGU","PEPE",
    "PERP","PHA","PLUME","PNUT","POL","POLIS","POLS","POND","PONKE","POPCAT",
    "PORTAL","POWR","PRCL","PRIME","PROVE","PSTAKE","PUFFER","PUMP","PYTH","QNT",
    "QTUM","RAD","RARE","RARI","RAY","RBC","RED","REN","RENDER","REP","REPV2",
    "REQ","REZ","RIZE","RLC","ROOK","RPL","RSR","RUNE","S","SAFE","SAMO","SAND",
    "SAPIEN","SBR","SC","SCRT","SDN","SGB","SHIB","SHX","SIGMA","SKY","SNX",
    "SOL","SONIC","SPELL","SPICE","SPX","SRM","STEP","STG","STORJ","STX","SUI",
    "SUNDOG","SUPER","SUSHI","SWARMS","SWELL","SYN","SYRUP","T","TBTC","TEER",
    "TLM","TNSR","TOKE","TOKEN","TON","TOSHI","TRAC","TRU","TRUMP","TRX","TURBO",
    "U","UFD","UMA","UNFI","UNI","USDC","USDQ","USDR","USELESS","UST","USUAL",
    "VANRY","VELODROME","VINE","VIRTUAL","VSN","VVV","W","WAL","WAVES","WBTC",
    "WELL","WEN","WIF","WLD","WOO","XCN","XDG","XLM","XNY","XRP","XRT","XTZ",
    "YFI","YGG","ZEREBRO","ZETA","ZEUS","ZEX","ZORA","ZRO","ZRX",
]

# Klíčová slova indikující důležitou změnu
# Primárně zachycují PŘED-událostní oznámení (delist, migrace, fork atd.)
KEYWORDS = [
    # Delisty
    "delist", "delisting", "removal", "will be removed", "trading pair removal",
    # Migrace a upgrady
    "migration", "migrate", "token swap", "chain migration", "network change",
    "network upgrade", "hard fork", "rebranding", "rebrand",
    # Zastavení obchodování / pozastavení
    "suspend", "suspension", "halt", "trading halt", "pause", "discontinu",
    "wind down", "end of support", "trading stopped",
    # Technické změny
    "swap", "upgrade", "deprecat", "sunset", "contract",
    # Obecná údržba (může předcházet delistu)
    "maintenance",
]

# Exchange announcement feed URLs
#
# STRATEGIE: Pro každou burzu monitorujeme jak hlavní blog, tak support/announcement centrum.
# Delistingy a migrace jsou VŽDY v announcement centru — blog může mít zpoždění nebo je vůbec nepostí.
# Příklad: Kraken oznámil migraci OM→MANTRA (únor 2026) pouze přes support centrum, ne blog.
#
# Pokrytí jednotlivých burz:
#   Kraken      → blog + Zendesk support centrum (kategorie Announcements)
#   Coinbase    → blog  [help.coinbase.com používá Intercom, RSS nedostupné]
#   Binance     → announcement RSS + delisting-specifická kategorie (navId=161)
#   OKX         → help center RSS (pokrývá všechny sekce vč. delistingů)
#   Bybit       → přímo announcements.bybit.com (= support centrum)
#   Crypto.com  → obecný feed  [exchange.crypto.com/announcements RSS nedostupné]
#   KuCoin      → news RSS + announcement RSS (dva oddělené endpointy)
#   Gate.io     → article RSS + announcement RSS (announcement centrum na gate.com)
#   MEXC        → blog  [support centrum bez RSS]
#   Huobi/HTX   → announcement RSS

EXCHANGE_FEEDS = {
    # ── Kraken ───────────────────────────────────────────────────────────────
    "Kraken":               "https://blog.kraken.com/feed",

    # ── Binance ──────────────────────────────────────────────────────────────
    "Binance":              "https://www.binance.com/en/support/announcement/rss",
    "BinanceDelisting":     "https://www.binance.com/en/support/announcement/rss?navId=161",

    # ── KuCoin ───────────────────────────────────────────────────────────────
    "KuCoin":               "https://www.kucoin.com/rss/news?lang=en_US",
}

# Zpravodajské RSS feedy — zachytí delistingy a migrace z médií
NEWS_FEEDS = {
    "CoinDesk":      "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Decrypt":       "https://decrypt.co/feed",
    "CoinTelegraph": "https://cointelegraph.com/rss",
}

# Veřejné Telegram kanály burz s announcement centry.
# Scrapujeme přes https://t.me/s/{channel} (web preview, bez autentizace).
# Pokud kanál neexistuje nebo se přejmenoval, scraper vrátí prázdný seznam.
TELEGRAM_CHANNELS = {
    "Bybit":      "BybitAnnouncements",
    "OKX":        "OKXAnnouncements",
    # Gate.io: zkouší GateioAnnouncements → gate_io → GateAnnouncements (viz scrape_telegram_gate)
    "Gate":       "GateioAnnouncements",
    "CryptoCom":  "CryptoComChannel",
    # HTX: zkouší HTXglobal → HTX_Global → HTX_Official (viz scrape_telegram_htx)
    "HTX":        "HTXglobal",
    "Coinbase":   "CoinbaseNewsletter",
}

# CoinMarketCap API key (volitelné – free tier stačí)
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")

# Kde ukládat stav a logy — lze přepsat env proměnnou (Fly.io volume: /data)
STATE_FILE = os.environ.get("STATE_FILE", "monitor_state.json")
LOG_FILE   = os.environ.get("LOG_FILE",   "monitor.log")
