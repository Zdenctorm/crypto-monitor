# ── KONFIGURACE ──────────────────────────────────────────────────────────────

import os

CRYPTOPANIC_API_KEY  = os.environ.get("CRYPTOPANIC_API_KEY", "")
TELEGRAM_BOT_TOKEN   = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID     = os.environ.get("TELEGRAM_CHAT_ID", "")

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

# ── RSS FEEDY (EXCHANGE_FEEDS) ────────────────────────────────────────────────
#
# Pouze ověřené funkční RSS feedy.
# Burzy BEZ RSS mají vlastní fetch funkce v crypto_monitor.py:
#   fetch_binance_api()      → Binance BAPI (RSS vrací 0 položek)
#   fetch_okx_api()          → OKX API v5  (RSS neexistuje)
#   fetch_kraken_support()   → Zendesk API (RSS blokováno)
#   fetch_bybit()            → Bybit V5 API (RSS blokováno)
#   fetch_htx_api()          → HTX Zendesk API (RSS blokováno)
#
# Výsledky health checku (2026-03-18) + stav po opravách:
#   Kraken blog     ✅ RSS funguje
#   KrakenSupport   → fetch_kraken_support() přes Zendesk API
#   Coinbase        → blog.coinbase.com/feed (Medium RSS, zkouší se s browser headers)
#   Binance         → fetch_binance_api() přes BAPI
#   OKX             → fetch_okx_api() přes API v5
#   Bybit           → fetch_bybit() přes V5 API  [již implementováno]
#   KuCoin news     ✅ RSS funguje (50 položek)
#   Gate.io         → RSS s browser headers (zkouší se)
#   HTX (Huobi)     → fetch_htx_api() přes Zendesk API

EXCHANGE_FEEDS = {
    # ── Kraken blog ───────────────────────────────────────────────────────────
    "Kraken":       "https://blog.kraken.com/feed",

    # ── Coinbase blog (Medium RSS) ────────────────────────────────────────────
    # blog.coinbase.com je Medium publikace → standard RSS feed.
    # Může selhat za Cloudflare — fetch_exchange_feeds() zkouší s browser headers.
    "Coinbase":     "https://blog.coinbase.com/feed",

    # ── KuCoin news ───────────────────────────────────────────────────────────
    "KuCoin":       "https://www.kucoin.com/rss/news?lang=en_US",

    # ── Gate.io ───────────────────────────────────────────────────────────────
    # RSS existuje ale při předchozím testu vrátilo malformed XML (Cloudflare).
    # Zkouší se s plnými browser headers — může fungovat z GitHub Actions.
    "Gate":         "https://www.gate.io/article/rss",
}

# CoinMarketCap API key (volitelné – free tier stačí)
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")

# Kde ukládat stav a logy
STATE_FILE = "monitor_state.json"
LOG_FILE   = "monitor.log"
