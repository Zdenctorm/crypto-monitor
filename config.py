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
    # POZOR: Migrace/delistingy jsou výhradně ve support centru, ne na blogu!
    # Příklad: OM→MANTRA migrace (únor 2026) byla pouze na support.kraken.com
    "Kraken":               "https://blog.kraken.com/feed",
    "KrakenSupport":        "https://support.kraken.com/hc/en-us/categories/200187583-Announcements/articles.rss",

    # ── Coinbase ─────────────────────────────────────────────────────────────
    # help.coinbase.com používá Intercom (ne Zendesk) → RSS nedostupné.
    # Delistingy a migrace jsou oznamovány na blogu i přes @CoinbaseAssets na X.
    "Coinbase":             "https://www.coinbase.com/blog/landing/rss",

    # ── Binance ──────────────────────────────────────────────────────────────
    # Hlavní announcement feed pokrývá vše; delisting kategorie (navId=161)
    # filtruje pouze delistingy → méně šumu, rychlejší záchyt.
    "Binance":              "https://www.binance.com/en/support/announcement/rss",
    "BinanceDelisting":     "https://www.binance.com/en/support/announcement/rss?navId=161",

    # ── OKX ──────────────────────────────────────────────────────────────────
    # Help center RSS pokrývá celý support vč. sekce Delistings & migrations.
    # Dedikovaná sekce: okx.com/help/section/announcements-delistings
    "OKX":                  "https://www.okx.com/help-center/rss",

    # ── Bybit ────────────────────────────────────────────────────────────────
    # announcements.bybit.com JE přímo support/announcement centrum (ne blog).
    # Pokrývá delistingy, maintenance, token migrace.
    "Bybit":                "https://announcements.bybit.com/en-US/rss/",

    # ── Crypto.com ───────────────────────────────────────────────────────────
    # crypto.com/exchange/announcements/list nemá RSS.
    # Obecný feed zachytí klíčová oznámení.
    "CryptoCom":            "https://crypto.com/en/feed/rss",

    # ── KuCoin ───────────────────────────────────────────────────────────────
    # Dva oddělené endpointy: news RSS a announcement RSS.
    # Announcement RSS (~kucoin.com/announcement) pokrývá delistingy přímo.
    "KuCoin":               "https://www.kucoin.com/rss/news?lang=en_US",
    "KuCoinAnnouncement":   "https://www.kucoin.com/rss/announcement?lang=en_US",

    # ── Gate.io ──────────────────────────────────────────────────────────────
    # article/rss = obecné články; announcement/rss = gate.com announcement centrum.
    # Delistingy na: gate.com/announcements/delisted
    "Gate":                 "https://www.gate.io/article/rss",
    "GateAnnouncement":     "https://www.gate.com/announcements/rss",

    # ── HTX (Huobi) ──────────────────────────────────────────────────────────
    # HTX je přejmenovaný Huobi; announcement centrum má vlastní RSS.
    "HTX":                  "https://www.htx.com/support/en-us/rss/",
}

# CoinMarketCap API key (volitelné – free tier stačí)
COINMARKETCAP_API_KEY = os.environ.get("COINMARKETCAP_API_KEY", "")

# Kde ukládat stav a logy
STATE_FILE = "monitor_state.json"
LOG_FILE   = "monitor.log"
