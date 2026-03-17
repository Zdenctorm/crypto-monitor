# ── KONFIGURACE ──────────────────────────────────────────────────────────────

import os

CRYPTOPANIC_API_KEY  = os.environ["CRYPTOPANIC_API_KEY"]
TELEGRAM_BOT_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID     = os.environ["TELEGRAM_CHAT_ID"]

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
KEYWORDS = [
    "delist", "delisting", "migration", "migrate", "swap", "upgrade",
    "deprecat", "sunset", "network upgrade", "contract", "hard fork",
    "maintenance", "suspend", "halt", "pause", "rebranding", "rebrand",
    "token swap", "chain migration", "network change", "discontinu",
]

# Exchange announcement feed URLs
EXCHANGE_FEEDS = {
    "Kraken":   "https://blog.kraken.com/feed",
    "Coinbase": "https://www.coinbase.com/blog/landing/rss",
    "Binance":  "https://www.binance.com/en/support/announcement/rss",
    "OKX":      "https://www.okx.com/help-center/rss",
}

# Kde ukládat stav a logy
STATE_FILE = "monitor_state.json"
LOG_FILE   = "monitor.log"
