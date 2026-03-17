# Contract addresses extracted from currency-config.ts
# Maps token symbol -> list of {platform, address} for CoinMarketCap lookups
# EVM addresses are lowercased; Solana/Tron addresses preserve original case

TOKEN_CONTRACTS: dict[str, list[dict]] = {
    '1INCH': [
        {'platform': 'ethereum', 'address': '0x111111111117dc0aa78b770fa6a738034120c302'},
    ],
    'AAVE': [
        {'platform': 'ethereum', 'address': '0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9'},
    ],
    'ACH': [
        {'platform': 'ethereum', 'address': '0xed04915c23f00a313a544955524eb7dbd823143d'},
    ],
    'ACT': [
        {'platform': 'solana', 'address': 'GJAFwWjJ3vnTsrQVabjBVK2TYB1YtRCQXRDfDgUnpump'},
    ],
    'ACX': [
        {'platform': 'ethereum', 'address': '0x44108f0223a3c3028f5fe7aec7f9bb2e66bef82f'},
    ],
    'ADX': [
        {'platform': 'ethereum', 'address': '0xade00c28244d5ce17d72e40330b1c318cd12b7c3'},
    ],
    'AERO': [
        {'platform': 'base', 'address': '0x940181a94a35a4569e4529a3cdfb74e38fd98631'},
    ],
    'AEVO': [
        {'platform': 'ethereum', 'address': '0xb528edbef013aff855ac3c50b381f253af13b997'},
    ],
    'AGLD': [
        {'platform': 'ethereum', 'address': '0x32353a6c91143bfd6c7d363b546e62a9a2489a20'},
    ],
    'AI16Z': [
        {'platform': 'solana', 'address': 'HeLp6NuQkmYB4pYWo2zYs22mESHXPQYzXbB8n4V98jwC'},
    ],
    'AIOZ': [
        {'platform': 'ethereum', 'address': '0x626e8036deb333b408be468f951bdb42433cbf18'},
    ],
    'AIXBT': [
        {'platform': 'base', 'address': '0x4f9fd6be4a90f2620860d680c0d4d5fb53d1a825'},
    ],
    'ALCX': [
        {'platform': 'ethereum', 'address': '0xdbdb4d16eda451d0503b854cf79d55697f90c8df'},
    ],
    'ALICE': [
        {'platform': 'ethereum', 'address': '0xac51066d7bec65dc4589368da368b212745d63e8'},
    ],
    'ALPHA': [
        {'platform': 'ethereum', 'address': '0xa1faa113cbe53436df28ff0aee54275c13b40975'},
    ],
    'ALT': [
        {'platform': 'ethereum', 'address': '0x8457ca5040ad67fdebbcc8edce889a335bc0fbfb'},
    ],
    'ANKR': [
        {'platform': 'ethereum', 'address': '0x8290333cef9e6d528dd5618fb97a76f268f3edd4'},
    ],
    'ANLOG': [
        {'platform': 'ethereum', 'address': '0xf983da3ca66964c02628189ea8ca99fa9e24f66c'},
    ],
    'ANON': [
        {'platform': 'solana', 'address': '9McvH6w97oewLmPxqQEoHUAv3u5iYMyQ9AeZZhguYf1T'},
    ],
    'ANT': [
        {'platform': 'ethereum', 'address': '0xa117000000f279d81a1d3cc75430faa017fa5a2e'},
    ],
    'APE': [
        {'platform': 'ethereum', 'address': '0x4d224452801aced8b2f0aebe155379bb5d594381'},
    ],
    'APENFT': [
        {'platform': 'tron', 'address': 'TFczxzPhnThNSqr5by8tvxsdCFRRz6cPNq'},
    ],
    'API3': [
        {'platform': 'ethereum', 'address': '0x0b38210ea11411557c13457d4da7dc6ea731b88a'},
    ],
    'APU': [
        {'platform': 'ethereum', 'address': '0x594daad7d77592a2b97b725a7ad59d7e188b5bfa'},
    ],
    'ARKM': [
        {'platform': 'ethereum', 'address': '0x6e2a43be0b1d33b726f0ca3b8de60b3482b8b050'},
    ],
    'ARPA': [
        {'platform': 'ethereum', 'address': '0xba50933c268f567bdc86e1ac131be072c6b0b71a'},
    ],
    'ATH': [
        {'platform': 'ethereum', 'address': '0xbe0ed4138121ecfc5c0e56b40517da27e6c5226b'},
    ],
    'ATLAS': [
        {'platform': 'solana', 'address': 'ATLASXmbPQxBUYbxPsV97usA3fPQYEqzQBUHgiFCUsXx'},
    ],
    'AUCTION': [
        {'platform': 'ethereum', 'address': '0xa9b1eb5908cfc3cdf91f9b8b3a74108598009096'},
    ],
    'AUDIO': [
        {'platform': 'ethereum', 'address': '0x18aaa7115705e8be94bffebde57af9bfc265b998'},
    ],
    'AVAAI': [
        {'platform': 'solana', 'address': 'DKu9kykSfbN5LBfFXtNNDPaX35o4Fv6vJ9FKk7pZpump'},
    ],
    'AVNT': [
        {'platform': 'base', 'address': '0x696f9436b67233384889472cd7cd58a6fb5df4f1'},
    ],
    'AXS': [
        {'platform': 'ethereum', 'address': '0xbb0e17ef65f82ab018d8edd776e8dd940327b28b'},
    ],
    'B3': [
        {'platform': 'base', 'address': '0xb3b32f9f8827d4634fe7d973fa1034ec9fddb3b3'},
    ],
    'BADGER': [
        {'platform': 'ethereum', 'address': '0x3472a5a71965499acd81997a54bba8d852c6e53d'},
    ],
    'BAL': [
        {'platform': 'ethereum', 'address': '0xba100000625a3754423978a60c9317c58a424e3d'},
    ],
    'BANANAS31': [
        {'platform': 'bsc', 'address': '0x3d4f0513e8a29669b960f9dbca61861548a9a760'},
    ],
    'BAND': [
        {'platform': 'ethereum', 'address': '0xba11d00c5f74255f56a5e366f4f77f5a186d7f55'},
    ],
    'BAT': [
        {'platform': 'ethereum', 'address': '0x0d8775f648430679a709e98d2b0cb6250d2887ef'},
    ],
    'BEAM': [
        {'platform': 'ethereum', 'address': '0x62d0a8458ed7719fdaf978fe5929c6d342b0bfce'},
    ],
    'BICO': [
        {'platform': 'ethereum', 'address': '0xf17e65822b568b3903685a7c9f496cf7656cc6c2'},
    ],
    'BIGTIME': [
        {'platform': 'ethereum', 'address': '0x64bc2ca1be492be7185faa2c8835d9b824c8a194'},
    ],
    'BIO': [
        {'platform': 'solana', 'address': 'bioJ9JTqW62MLz7UKHU69gtKhPpGi1BQhccj2kmSvUJ'},
    ],
    'BIT': [
        {'platform': 'ethereum', 'address': '0x1a4b46696b2bb4794eb3d4c26f1c55f9170fa4c5'},
    ],
    'BLUR': [
        {'platform': 'ethereum', 'address': '0x5283d291dbcf85356a21ba090e6db59121208b44'},
    ],
    'BLZ': [
        {'platform': 'ethereum', 'address': '0x5732046a883704404f284ce41ffadd5b007fd668'},
    ],
    'BMT': [
        {'platform': 'solana', 'address': 'FQgtfugBdpFN7PZ6NdPrZpVLDBrPGxXesi4gVu3vErhY'},
    ],
    'BNT': [
        {'platform': 'ethereum', 'address': '0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c'},
    ],
    'BOBA': [
        {'platform': 'ethereum', 'address': '0x42bbfa2e77757c645eeaad1655e0911a7553efbc'},
    ],
    'BOND': [
        {'platform': 'ethereum', 'address': '0x0391d2021f89dc339f60fff84546ea23e337750f'},
    ],
    'BONK': [
        {'platform': 'solana', 'address': 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263'},
    ],
    'BTT': [
        {'platform': 'tron', 'address': 'TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4'},
    ],
    'C98': [
        {'platform': 'ethereum', 'address': '0xae12c5930881c53715b369cec7606b70d8eb229f'},
    ],
    'CAKE': [
        {'platform': 'bsc', 'address': '0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'},
    ],
    'CELR': [
        {'platform': 'ethereum', 'address': '0x4f9254c83eb525f9fcf346490bbb3ed28a81c667'},
    ],
    'CFG': [
        {'platform': 'ethereum', 'address': '0xcccccccccc33d538dbc2ee4feab0a7a1ff4e8a94'},
    ],
    'CHEEMS': [
        {'platform': 'bsc', 'address': '0x0df0587216a4a1bb7d5082fdc491d93d2dd4b413'},
    ],
    'CHEX': [
        {'platform': 'ethereum', 'address': '0x9ce84f6a69986a83d92c324df10bc8e64771030f'},
    ],
    'CHR': [
        {'platform': 'ethereum', 'address': '0x8a2279d4a90b6fe1c4b30fa660cc9f926797baa2'},
    ],
    'CHZ': [
        {'platform': 'ethereum', 'address': '0x3506424f91fd33084466f402d5d97f05f8e3b4af'},
    ],
    'CLOUD': [
        {'platform': 'solana', 'address': 'CLoUDKc4Ane7HeQcPpE3YHnznRxhMimJ4MyaUqyHFzAu'},
    ],
    'CLV': [
        {'platform': 'ethereum', 'address': '0x80c62fe4487e1351b47ba49809ebd60ed085bf52'},
    ],
    'COMP': [
        {'platform': 'ethereum', 'address': '0xc00e94cb662c3520282e6f5717214004a7f26888'},
    ],
    'COOKIE': [
        {'platform': 'bsc', 'address': '0xc0041ef357b183448b235a8ea73ce4e4ec8c265f'},
    ],
    'COTI': [
        {'platform': 'ethereum', 'address': '0xddb3422497e61e13543bea06989c0789117555c5'},
    ],
    'COW': [
        {'platform': 'ethereum', 'address': '0xdef1ca1fb7fbcdc777520aa7f396b4e015f497ab'},
    ],
    'CPOOL': [
        {'platform': 'ethereum', 'address': '0x66761fa41377003622aee3c7675fc7b5c1c2fac5'},
    ],
    'CQT': [
        {'platform': 'ethereum', 'address': '0xd417144312dbf50465b1c641d016962017ef6240'},
    ],
    'CRO': [
        {'platform': 'ethereum', 'address': '0xa0b73e1ff0b80914ab6fe0444e65848c4c34450b'},
    ],
    'CRV': [
        {'platform': 'ethereum', 'address': '0xd533a949740bb3306d119cc777fa900ba034cd52'},
    ],
    'CTSI': [
        {'platform': 'ethereum', 'address': '0x491604c0fdf08347dd1fa4ee062a822a5dd06b5d'},
    ],
    'CVC': [
        {'platform': 'ethereum', 'address': '0x41e5560054824ea6b0732e656e3ad64e20e94e45'},
    ],
    'CVX': [
        {'platform': 'ethereum', 'address': '0x4e3fbd56cd56c3e72c1403e103b45db9da5b9d2b'},
    ],
    'CXT': [
        {'platform': 'ethereum', 'address': '0x7abc8a5768e6be61a6c693a6e4eacb5b60602c4d'},
    ],
    'CYBER': [
        {'platform': 'optimism', 'address': '0x14778860e937f509e651192a90589de711fb88a9'},
    ],
    'DAI': [
        {'platform': 'ethereum', 'address': '0x6b175474e89094c44da98b954eedeac495271d0f'},
        {'platform': 'arbitrum-one', 'address': '0xda10009cbd5d07dd0cecc66161fc93d7c9000da1'},
        {'platform': 'polygon', 'address': '0x8f3cf7ad23cd3cadbd9735aff958023239c6a063'},
    ],
    'DBR': [
        {'platform': 'solana', 'address': 'DBRiDgJAMsM95moTzJs7M9LnkGErpbv9v6CUR1DXnUu5'},
    ],
    'DENT': [
        {'platform': 'ethereum', 'address': '0x3597bfd533a99c9aa083587b074434e61eb0a258'},
    ],
    'DRIFT': [
        {'platform': 'solana', 'address': 'DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7'},
    ],
    'DRV': [
        {'platform': 'ethereum', 'address': '0xb1d1eae60eea9525032a6dcb4c1ce336a1de71be'},
    ],
    'DYDX': [
        {'platform': 'ethereum', 'address': '0x92d6c1e31e14520e676a687f0a93788b716beff5'},
    ],
    'EIGEN': [
        {'platform': 'ethereum', 'address': '0xec53bf9167f50cdeb3ae105f56099aaab9061f83'},
    ],
    'ELIZAOS': [
        {'platform': 'solana', 'address': 'DuMbhu7mvQvqQHGcnikDgb4XegXJRyhUBfdU22uELiZA'},
    ],
    'ELX': [
        {'platform': 'ethereum', 'address': '0x89a8c847f41c0dfa6c8b88638bacca8a0b777da7'},
    ],
    'ENA': [
        {'platform': 'ethereum', 'address': '0x57e114b691db790c35207b2e685d4a43181e6061'},
    ],
    'ENJ': [
        {'platform': 'ethereum', 'address': '0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c'},
    ],
    'ENS': [
        {'platform': 'ethereum', 'address': '0xc18360217d8f7ab5e7c516566761ea12ce7f9d72'},
    ],
    'ENSO': [
        {'platform': 'ethereum', 'address': '0x699f088b5dddcafb7c4824db5b10b57b37cb0c66'},
    ],
    'ESX': [
        {'platform': 'base', 'address': '0x6a72d3a87f97a0fee2c2ee4233bdaebc32813d7a'},
    ],
    'ETH': [
        {'platform': 'arbitrum-one', 'address': '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'},
    ],
    'ETHFI': [
        {'platform': 'ethereum', 'address': '0xfe0c30065b384f05761f15d0cc899d4f9f9cc0eb'},
    ],
    'EUL': [
        {'platform': 'ethereum', 'address': '0xd9fcd98c322942075a5c3860693e9f4f03aae07b'},
    ],
    'EURC': [
        {'platform': 'ethereum', 'address': '0x1abaea1f7c830bd89acc67ec4af516284b1bc33c'},
    ],
    'EURR': [
        {'platform': 'ethereum', 'address': '0x50753cfaf86c094925bf976f218d043f8791e408'},
    ],
    'FARM': [
        {'platform': 'ethereum', 'address': '0xa0246c9032bc3a600820415ae600c6388619a14d'},
    ],
    'FARTCOIN': [
        {'platform': 'solana', 'address': '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'},
    ],
    'FHE': [
        {'platform': 'ethereum', 'address': '0xd55c9fb62e176a8eb6968f32958fefdd0962727e'},
    ],
    'FIDA': [
        {'platform': 'solana', 'address': 'EchesyfXePKdLtoiZSL8pBe8Myagyy8ZRqsACNCFGnvp'},
    ],
    'FIS': [
        {'platform': 'ethereum', 'address': '0xef3a930e1ffffacd2fc13434ac81bd278b0ecc8d'},
    ],
    'FLOKI': [
        {'platform': 'ethereum', 'address': '0xcf0c122c6b73ff809c693db761e7baebe62b6a2e'},
    ],
    'FLUX': [
        {'platform': 'ethereum', 'address': '0x720cd16b011b987da3518fbf38c3071d4f0d1495'},
    ],
    'FORTH': [
        {'platform': 'ethereum', 'address': '0x77fba179c79de5b7653f68b5039af940ada60ce0'},
    ],
    'FWOG': [
        {'platform': 'solana', 'address': 'A8C3xuqscfmyLrte3VmTqrAq8kgMASius9AFNANwpump'},
    ],
    'FXS': [
        {'platform': 'ethereum', 'address': '0x3432b6a60d23ca0dfca7761b7ab56459d9c964d0'},
    ],
    'G': [
        {'platform': 'ethereum', 'address': '0x9c7beba8f6ef6643abd725e45a4e8387ef260649'},
    ],
    'GAL': [
        {'platform': 'ethereum', 'address': '0x5faa989af96af85384b8a938c2ede4a7378d9875'},
    ],
    'GALA': [
        {'platform': 'ethereum', 'address': '0xd1d2eb1b1e90b638588728b4130137d262c87cae'},
    ],
    'GARI': [
        {'platform': 'solana', 'address': 'CKaKtYvz6dKPyMvYq9Rh3UBrnNqYZAyd7iF4hJtjUvks'},
    ],
    'GFI': [
        {'platform': 'ethereum', 'address': '0xdab396ccf3d84cf2d07c4454e10c8a6f5b008d2b'},
    ],
    'GHST': [
        {'platform': 'ethereum', 'address': '0x3f382dbd960e3a9bbceae22651e88158d2791550'},
    ],
    'GIGA': [
        {'platform': 'solana', 'address': '63LfDmNb3MQ8mw9MtZ2To9bEA2M71kZUUGq5tiJxcqj9'},
    ],
    'GMT': [
        {'platform': 'solana', 'address': '7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx'},
    ],
    'GMX': [
        {'platform': 'arbitrum-one', 'address': '0xfc5a1a6eb076a2c7ad06ed22c90d7e710e35ad0a'},
    ],
    'GNO': [
        {'platform': 'ethereum', 'address': '0x6810e776880c02933d47db1b9fc05908e5386b96'},
    ],
    'GOAT': [
        {'platform': 'solana', 'address': 'CzLSujWBLFsSjncfkh59rUFqvafWcY5tzedWJSuypump'},
    ],
    'GOMINING': [
        {'platform': 'ethereum', 'address': '0x7ddc52c4de30e94be3a6a0a2b259b2850f421989'},
    ],
    'GRASS': [
        {'platform': 'solana', 'address': 'Grass7B4RdKfBCjTKgSqnXkqjwiGvQyFbuSCUJr3XXjs'},
    ],
    'GRIFFAIN': [
        {'platform': 'solana', 'address': 'KENJSUYLASHUMfHyy5o4Hp2FdNqZg1AsUPhfH2kYvEP'},
    ],
    'GRT': [
        {'platform': 'ethereum', 'address': '0xc944e90c64b2c07662a292be6244bdf05cda44a7'},
    ],
    'GST': [
        {'platform': 'solana', 'address': 'AFbX8oGjGpmVFywbVouvhQSRmiW2aR1mohfahi4Y2AdB'},
    ],
    'GTC': [
        {'platform': 'ethereum', 'address': '0xde30da39c46104798bb5aa3fe8b9e0e1f348163f'},
    ],
    'H': [
        {'platform': 'ethereum', 'address': '0xcf5104d094e3864cfcbda43b82e1cefd26a016eb'},
    ],
    'HFT': [
        {'platform': 'ethereum', 'address': '0xb3999f658c0391d94a37f7ff328f3fec942bcadc'},
    ],
    'HNT': [
        {'platform': 'solana', 'address': 'hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux'},
    ],
    'HONEY': [
        {'platform': 'solana', 'address': '4vMsoUT2BWatFweudnQM1xedRLfJgJ7hswhcpz4xgBTy'},
    ],
    'HPOS10I': [
        {'platform': 'ethereum', 'address': '0x72e4f9f808c49a2a61de9c5896298920dc4eeea9'},
    ],
    'IDEX': [
        {'platform': 'ethereum', 'address': '0xb705268213d593b8fd88d3fdeff93aff5cbdcfae'},
    ],
    'IMX': [
        {'platform': 'ethereum', 'address': '0xf57e7e7c23978c3caec3c3548e3d615c346e79ff'},
    ],
    'JAILSTOOL': [
        {'platform': 'solana', 'address': 'AxriehR6Xw3adzHopnvMn7GcpRFcD41ddpiTWMg6pump'},
    ],
    'JASMY': [
        {'platform': 'ethereum', 'address': '0x7420b4b9a0110cdc71fb720908340c03f9bc03ec'},
    ],
    'JTO': [
        {'platform': 'solana', 'address': 'jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL'},
    ],
    'JUP': [
        {'platform': 'solana', 'address': 'JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN'},
    ],
    'KAITO': [
        {'platform': 'base', 'address': '0x98d0baa52b2d063e780de12f615f963fe8537553'},
    ],
    'KEEP': [
        {'platform': 'ethereum', 'address': '0x85eee30c52b0b379b046fb0f85f4f3dc3009afec'},
    ],
    'KERNEL': [
        {'platform': 'ethereum', 'address': '0x3f80b1c54ae920be41a77f8b902259d48cf24ccf'},
    ],
    'KEY': [
        {'platform': 'ethereum', 'address': '0x4cc19356f2d37338b9802aa8e8fc58b0373296e7'},
    ],
    'KIN': [
        {'platform': 'solana', 'address': 'kinXdEcpDQeHPEuQnqmUgtYykqKGVFq6CeVX5iAHJq6'},
    ],
    'KMNO': [
        {'platform': 'solana', 'address': 'KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS'},
    ],
    'KNC': [
        {'platform': 'ethereum', 'address': '0xdefa4e8a7bcba345f687a2f1456f5edd9ce97202'},
    ],
    'KP3R': [
        {'platform': 'ethereum', 'address': '0x1ceb5cb57c4d4e2b2433641b95dd330a33185a44'},
    ],
    'KTA': [
        {'platform': 'base', 'address': '0xc0634090f2fe6c6d75e61be2b949464abb498973'},
    ],
    'L3': [
        {'platform': 'ethereum', 'address': '0x88909d489678dd17aa6d9609f89b0419bf78fd9a'},
    ],
    'LAYER': [
        {'platform': 'solana', 'address': 'LAYER4xPpTCb3QL8S9u41EAhAX7mhBn8Q6xMTwY2Yzc'},
    ],
    'LCX': [
        {'platform': 'ethereum', 'address': '0x037a54aab062628c9bbae1fdb1583c195585fe41'},
    ],
    'LDO': [
        {'platform': 'ethereum', 'address': '0x5a98fcbea516cf06857215779fd812ca3bef1b32'},
    ],
    'LINK': [
        {'platform': 'ethereum', 'address': '0x514910771af9ca656af840dff83e8264ecf986ca'},
    ],
    'LMWR': [
        {'platform': 'ethereum', 'address': '0x628a3b2e302c7e896acc432d2d0dd22b6cb9bc88'},
    ],
    'LOCKIN': [
        {'platform': 'solana', 'address': '8Ki8DpuWNxu9VsS3kQbarsCWMcFGWkzzA8pUPto9zBd5'},
    ],
    'LPT': [
        {'platform': 'ethereum', 'address': '0x58b6a8a3302369daec383334672404ee733ab239'},
    ],
    'LQTY': [
        {'platform': 'ethereum', 'address': '0x6dea81c8171d0ba574754ef6f8b412f2ed88c54d'},
    ],
    'LRC': [
        {'platform': 'ethereum', 'address': '0xbbbbca6a901c926f240b89eacb641d8aec7aeafd'},
    ],
    'LSETH': [
        {'platform': 'ethereum', 'address': '0x8c1bed5b9a0928467c9b1341da1d7bd5e10b6549'},
    ],
    'LSK': [
        {'platform': 'ethereum', 'address': '0x6033f7f88332b8db6ad452b7c6d5bb643990ae3f'},
    ],
    'M': [
        {'platform': 'bsc', 'address': '0x22b1458e780f8fa71e2f84502cee8b5a3cc731fa'},
    ],
    'MANA': [
        {'platform': 'ethereum', 'address': '0x0f5d2fb29fb7d3cfee444a200298f468908cc942'},
    ],
    'MASK': [
        {'platform': 'ethereum', 'address': '0x69af81e73a73b40adf4f3d4223cd9b1ece623074'},
    ],
    'MATIC': [
        {'platform': 'ethereum', 'address': '0x7d1afa7b718fb893db30a3abc0cfc608aacfebb0'},
    ],
    'MC': [
        {'platform': 'ethereum', 'address': '0x949d48eca67b17269629c7194f4b727d4ef9e5d6'},
    ],
    'ME': [
        {'platform': 'solana', 'address': 'MEFNBXixkEbait3xn9bkm8WsJzXtVsaJEn4c8Sam21u'},
    ],
    'MELANIA': [
        {'platform': 'solana', 'address': 'FUAfBo2jgks6gB4Z4LfZkqSZgzNucisEHqnNebaRxM1P'},
    ],
    'MEME': [
        {'platform': 'ethereum', 'address': '0xb131f4a55907b10d1f0a50d8ab8fa09ec342cd74'},
    ],
    'MERL': [
        {'platform': 'bsc', 'address': '0xa0c56a8c0692bd10b3fa8f8ba79cf5332b7107f9'},
    ],
    'MEW': [
        {'platform': 'solana', 'address': 'MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5'},
    ],
    'MICHI': [
        {'platform': 'solana', 'address': '5mbK36SZ7J19An8jFochhQS4of8g6BwUjbeCSxBSoWdp'},
    ],
    'MIR': [
        {'platform': 'ethereum', 'address': '0x09a3ecafa817268f77be1283176b946c4ff2e608'},
    ],
    'MIRROR': [
        {'platform': 'base', 'address': '0xe1bfa25468af64e366ddafc9d91bcc6c97439a14'},
    ],
    'MKR': [
        {'platform': 'ethereum', 'address': '0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2'},
    ],
    'MLN': [
        {'platform': 'ethereum', 'address': '0xec67005c4e498ec7f55e092bd1d35cbc47c91892'},
    ],
    'MNGO': [
        {'platform': 'solana', 'address': 'MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac'},
    ],
    'MNT': [
        {'platform': 'ethereum', 'address': '0x3c3a81e81dc49a522a592e7622a7e711c06bf354'},
    ],
    'MOG': [
        {'platform': 'ethereum', 'address': '0xaaee1a9723aadb7afa2810263653a34ba2c21c7a'},
    ],
    'MOODENG': [
        {'platform': 'solana', 'address': 'ED5nyyWEzpPPiWimP8vYm7sD7TD3LAt3Q3gRTWHzPJBY'},
    ],
    'MORPHO': [
        {'platform': 'ethereum', 'address': '0x58d97b57bb95320f9a05dc918aef65434969c2b2'},
    ],
    'MOVE': [
        {'platform': 'ethereum', 'address': '0x3073f7aaa4db83f95e9fff17424f71d4751a3073'},
    ],
    'MSOL': [
        {'platform': 'solana', 'address': 'mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So'},
    ],
    'MUBARAK': [
        {'platform': 'bsc', 'address': '0x5c85d6c6825ab4032337f11ee92a72df936b46f6'},
    ],
    'MULTI': [
        {'platform': 'ethereum', 'address': '0x65ef703f5594d2573eb71aaf55bc0cb548492df4'},
    ],
    'MV': [
        {'platform': 'ethereum', 'address': '0xae788f80f2756a86aa2f410c651f2af83639b95b'},
    ],
    'MXC': [
        {'platform': 'ethereum', 'address': '0x5ca381bbfb58f0092df149bd3d243b08b9a8386e'},
    ],
    'NEIRO': [
        {'platform': 'ethereum', 'address': '0x812ba41e071c7b7fa4ebcfb62df5f45f6fa853ee'},
    ],
    'NMR': [
        {'platform': 'ethereum', 'address': '0x1776e1f26f98b1a5df9cd347953a26dd3cb46671'},
    ],
    'NOBODY': [
        {'platform': 'solana', 'address': 'C29ebrgYjYoJPMGPnPSGY1q3mMGk4iDSqnQeQQA7moon'},
    ],
    'NOS': [
        {'platform': 'solana', 'address': 'nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7'},
    ],
    'NPC': [
        {'platform': 'ethereum', 'address': '0x8ed97a637a790be1feff5e888d43629dc05408f6'},
    ],
    'OCEAN': [
        {'platform': 'ethereum', 'address': '0x967da4048cd07ab37855c090aaf366e4ce1b9f48'},
    ],
    'ODOS': [
        {'platform': 'base', 'address': '0xca73ed1815e5915489570014e024b7ebe65de679'},
    ],
    'OGN': [
        {'platform': 'ethereum', 'address': '0x8207c1ffc5b6804f6024322ccf34f29c3541ae26'},
    ],
    'OMG': [
        {'platform': 'ethereum', 'address': '0xd26114cd6ee289accf82350c8d8487fedb8a0c07'},
    ],
    'OMNI': [
        {'platform': 'ethereum', 'address': '0x36e66fbbce51e4cd5bd3c62b637eb411b18949d4'},
    ],
    'ONDO': [
        {'platform': 'ethereum', 'address': '0xfaba6f8e4a5e8ab82f62fe7c39859fa577269be3'},
    ],
    'OOB': [
        {'platform': 'solana', 'address': 'oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo'},
    ],
    'OP': [
        {'platform': 'optimism', 'address': '0x4200000000000000000000000000000000000042'},
    ],
    'OPEN': [
        {'platform': 'ethereum', 'address': '0xa227cc36938f0c9e09ce0e64dfab226cad739447'},
    ],
    'ORCA': [
        {'platform': 'solana', 'address': 'orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE'},
    ],
    'OXT': [
        {'platform': 'ethereum', 'address': '0x4575f41308ec1483f3d399aa9a2826d74da13deb'},
    ],
    'OXY': [
        {'platform': 'solana', 'address': 'z3dn17yLaGMKffVogeFHQ9zWVcXgqgf3PQnDsNs2g6M'},
    ],
    'PAXG': [
        {'platform': 'ethereum', 'address': '0x45804880de22913dafe09f4980848ece6ecbaf78'},
    ],
    'PENDLE': [
        {'platform': 'ethereum', 'address': '0x808507121b80c02388fad14726482e061b8da827'},
    ],
    'PENGU': [
        {'platform': 'solana', 'address': '2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv'},
    ],
    'PEPE': [
        {'platform': 'ethereum', 'address': '0x6982508145454ce325ddbe47a25d4ec3d2311933'},
    ],
    'PERP': [
        {'platform': 'ethereum', 'address': '0xbc396689893d065f41bc2c6ecbee5e0085233447'},
    ],
    'PLA': [
        {'platform': 'ethereum', 'address': '0x3fa400483487a489ec9b1db29c4129063eec4654'},
    ],
    'PLUME': [
        {'platform': 'ethereum', 'address': '0x4c1746a800d224393fe2470c70a35717ed4ea5f1'},
    ],
    'PNUT': [
        {'platform': 'solana', 'address': '2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump'},
    ],
    'POLIS': [
        {'platform': 'solana', 'address': 'poLisWXnNRwC6oBu1vHiuKQzFjGL4XDSu4g9qjz9qVk'},
    ],
    'POLS': [
        {'platform': 'ethereum', 'address': '0x83e6f1e41cdd28eaceb20cb649155049fac3d5aa'},
    ],
    'POND': [
        {'platform': 'ethereum', 'address': '0x57b946008913b82e4df85f501cbaed910e58d26c'},
    ],
    'PONKE': [
        {'platform': 'solana', 'address': '5z3EqYQo9HiCEs3R84RCDMu2n7anpDMxRhdK8PSWmrRC'},
    ],
    'POPCAT': [
        {'platform': 'solana', 'address': '7GCihgDB8fe6KNjn2MYtkzZcRjQy3t9GHdC8uHYmW2hr'},
    ],
    'PORTAL': [
        {'platform': 'ethereum', 'address': '0x1bbe973bef3a977fc51cbed703e8ffdefe001fed'},
    ],
    'POWR': [
        {'platform': 'ethereum', 'address': '0x595832f8fc6bf59c85c527fec3740a1b7a361269'},
    ],
    'PRCL': [
        {'platform': 'solana', 'address': '4LLbsb5ReP3yEtYzmXewyGjcir5uXtKFURtaEUVC2AHs'},
    ],
    'PRIME': [
        {'platform': 'ethereum', 'address': '0xb23d80f5fefcddaa212212f028021b41ded428cf'},
    ],
    'PROVE': [
        {'platform': 'ethereum', 'address': '0x6bef15d938d4e72056ac92ea4bdd0d76b1c4ad29'},
    ],
    'PSTAKE': [
        {'platform': 'ethereum', 'address': '0xfb5c6815ca3ac72ce9f5006869ae67f18bf77006'},
    ],
    'PTB': [
        {'platform': 'ethereum', 'address': '0x30a25cc9c9eade4d4d9e9349be6e68c3411367d3'},
    ],
    'PUFFER': [
        {'platform': 'ethereum', 'address': '0x4d1c297d39c5c1277964d0e3f8aa901493664530'},
    ],
    'PUMP': [
        {'platform': 'solana', 'address': 'pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn'},
    ],
    'PYTH': [
        {'platform': 'solana', 'address': 'HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3'},
    ],
    'Q': [
        {'platform': 'ethereum', 'address': '0xc07e1300dc138601fa6b0b59f8d0fa477e690589'},
    ],
    'QNT': [
        {'platform': 'ethereum', 'address': '0x4a220e6096b25eadb88358cb44068a3248254675'},
    ],
    'RAD': [
        {'platform': 'ethereum', 'address': '0x31b595e7cfdb624d10a3e7a562ed98c3567e3865'},
    ],
    'RARE': [
        {'platform': 'ethereum', 'address': '0xba5bde662c17e2adff1075610382b9b691296350'},
    ],
    'RARI': [
        {'platform': 'ethereum', 'address': '0xfca59cd816ab1ead66534d82bc21e7515ce441cf'},
    ],
    'RAY': [
        {'platform': 'solana', 'address': '4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R'},
    ],
    'RBC': [
        {'platform': 'ethereum', 'address': '0x3330bfb7332ca23cd071631837dc289b09c33333'},
    ],
    'RED': [
        {'platform': 'ethereum', 'address': '0xc43c6bfeda065fe2c4c11765bf838789bd0bb5de'},
    ],
    'REN': [
        {'platform': 'ethereum', 'address': '0x408e41876cccdc0f92210600ef50372656052a38'},
    ],
    'RENDER': [
        {'platform': 'solana', 'address': 'rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof'},
    ],
    'REP': [
        {'platform': 'ethereum', 'address': '0x1985365e9f78359a9b6ad760e32412f4a445e862'},
    ],
    'REPV2': [
        {'platform': 'ethereum', 'address': '0x221657776846890989a759ba2973e427dff5c9bb'},
    ],
    'REQ': [
        {'platform': 'ethereum', 'address': '0x8f8221afbb33998d8584a2b05749ba73c37a938a'},
    ],
    'REZ': [
        {'platform': 'ethereum', 'address': '0x3b50805453023a91a8bf641e279401a0b23fa6f9'},
    ],
    'RIZE': [
        {'platform': 'base', 'address': '0x9818b6c09f5ecc843060927e8587c427c7c93583'},
    ],
    'RLC': [
        {'platform': 'ethereum', 'address': '0x607f4c5bb672230e8672085532f7e901544a7375'},
    ],
    'RNDR': [
        {'platform': 'ethereum', 'address': '0x6de037ef9ad2725eb40118bb1702ebb27e4aeb24'},
    ],
    'ROOK': [
        {'platform': 'ethereum', 'address': '0xfa5047c9c78b8877af97bdcb85db743fd7313d4a'},
    ],
    'RPL': [
        {'platform': 'ethereum', 'address': '0xd33526068d116ce69f19a9ee46f0bd304f21a51f'},
    ],
    'RSR': [
        {'platform': 'ethereum', 'address': '0x320623b8e4ff03373931769a31fc52a4e78b5d70'},
    ],
    'SAFE': [
        {'platform': 'ethereum', 'address': '0x5afe3855358e112b5647b952709e6165e1c1eeee'},
    ],
    'SAMO': [
        {'platform': 'solana', 'address': '7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU'},
    ],
    'SAND': [
        {'platform': 'ethereum', 'address': '0x3845badade8e6dff049820680d1f14bd3903a5d0'},
    ],
    'SAPIEN': [
        {'platform': 'base', 'address': '0xc729777d0470f30612b1564fd96e8dd26f5814e3'},
    ],
    'SBR': [
        {'platform': 'solana', 'address': 'Saber2gLauYim4Mvftnrasomsv6NvAuncvMEZwcLpD1'},
    ],
    'SHIB': [
        {'platform': 'ethereum', 'address': '0x95ad61b0a150d79219dcf64e1e6cc01f0b64c4ce'},
    ],
    'SHX': [
        {'platform': 'ethereum', 'address': '0x516d31321928700c6b4fb0db0c8c6bc5d6799787'},
    ],
    'SIGMA': [
        {'platform': 'solana', 'address': '5SVG3T9CNQsm2kEwzbRq6hASqh1oGfjqTtLXYUibpump'},
    ],
    'SKY': [
        {'platform': 'ethereum', 'address': '0x56072c95faa701256059aa122697b133aded9279'},
    ],
    'SNX': [
        {'platform': 'ethereum', 'address': '0xc011a73ee8576fb46f5e1c5751ca3b9fe0af2a6f'},
    ],
    'SONIC': [
        {'platform': 'solana', 'address': 'SonicxvLud67EceaEzCLRnMTBqzYUUYNr93DBkBdDES'},
    ],
    'SPELL': [
        {'platform': 'ethereum', 'address': '0x090185f2135308bad17527004364ebcc2d37e5f6'},
    ],
    'SPICE': [
        {'platform': 'solana', 'address': 'SPQkEcsdALLLn4MqCb3XH64hYTmdD4fZZk9CF5LiQV8'},
    ],
    'SPX': [
        {'platform': 'ethereum', 'address': '0xe0f63a424a4439cbe457d80e4f4b51ad25b2c56c'},
    ],
    'SRM': [
        {'platform': 'solana', 'address': 'SRMuApVNdxXokk5GT7XD5cUUgXMBCoAz2LHeuAoKWRt'},
    ],
    'STEP': [
        {'platform': 'solana', 'address': 'StepAscQoEioFxxWGnh2sLBDFp9d8rvKz2Yp39iDpyT'},
    ],
    'STG': [
        {'platform': 'ethereum', 'address': '0xaf5191b0de278c7286d6c7cc6ab6bb8a73ba2cd6'},
    ],
    'STORJ': [
        {'platform': 'ethereum', 'address': '0xb64ef51c888972c908cfacf59b47c1afbc0ab8ac'},
    ],
    'SUNDOG': [
        {'platform': 'tron', 'address': 'TXL6rJbvmjD46zeN1JssfgxvSo99qC8MRT'},
    ],
    'SUPER': [
        {'platform': 'ethereum', 'address': '0xe53ec727dbdeb9e2d5456c3be40cff031ab40a55'},
    ],
    'SUSHI': [
        {'platform': 'ethereum', 'address': '0x6b3595068778dd592e39a122f4f5a5cf09c90fe2'},
    ],
    'SWARMS': [
        {'platform': 'solana', 'address': '74SBV4zDXxTRgv1pEMoECskKBkZHc2yGPnc7GYVepump'},
    ],
    'SWELL': [
        {'platform': 'ethereum', 'address': '0x0a6e7ba5042b38349e437ec6db6214aec7b35676'},
    ],
    'SYN': [
        {'platform': 'ethereum', 'address': '0x0f2d719407fdbeff09d87557abb7232601fd9f29'},
    ],
    'SYRUP': [
        {'platform': 'ethereum', 'address': '0x643c4e15d7d62ad0abec4a9bd4b001aa3ef52d66'},
    ],
    'T': [
        {'platform': 'ethereum', 'address': '0xf7920b0768ecb20a123fac32311d07d193381d6f'},
    ],
    'TBTC': [
        {'platform': 'ethereum', 'address': '0x8daebade922df735c38c80c7ebd708af50815faa'},
    ],
    'TLM': [
        {'platform': 'ethereum', 'address': '0x888888848b652b3e3a0f34c96e00eec0f3a23f72'},
    ],
    'TNSR': [
        {'platform': 'solana', 'address': 'TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6'},
    ],
    'TOKE': [
        {'platform': 'ethereum', 'address': '0x2e9d63788249371f1dfc918a52f8d799f4a38c94'},
    ],
    'TOKEN': [
        {'platform': 'ethereum', 'address': '0x4507cef57c46789ef8d1a19ea45f4216bae2b528'},
    ],
    'TOSHI': [
        {'platform': 'base', 'address': '0xac1bd2486aaf3b5c0fc3fd868558b082a531b2b4'},
    ],
    'TRAC': [
        {'platform': 'ethereum', 'address': '0xaa7a9ca87d3694b5755f213b5d04094b8d0f0a6f'},
    ],
    'TRIBE': [
        {'platform': 'ethereum', 'address': '0xc7283b66eb1eb5fb86327f08e1b5816b0720212b'},
    ],
    'TRU': [
        {'platform': 'ethereum', 'address': '0x4c19596f5aaff459fa38b0f7ed92f11ae6543784'},
    ],
    'TRUMP': [
        {'platform': 'solana', 'address': '6p6xgHyF7AeE6TZkSmFsko444wqoP15icUSqi2jfGiPN'},
    ],
    'TURBO': [
        {'platform': 'ethereum', 'address': '0xa35923162c49cf95e6bf26623385eb431ad920d3'},
    ],
    'TVK': [
        {'platform': 'ethereum', 'address': '0xd084b83c305dafd76ae3e1b4e1f1fe2ecccb3988'},
    ],
    'U': [
        {'platform': 'ethereum', 'address': '0xba5ed44733953d79717f6269357c77718c8ba5ed'},
    ],
    'UFD': [
        {'platform': 'solana', 'address': 'eL5fUxj2J4CiQsmW85k5FG9DvuQjjUoBHoQBi2Kpump'},
    ],
    'UMA': [
        {'platform': 'ethereum', 'address': '0x04fa0d235c4abf4bcf4787af4cf447de572ef828'},
    ],
    'UNFI': [
        {'platform': 'ethereum', 'address': '0x441761326490cacf7af299725b6292597ee822c2'},
    ],
    'UNI': [
        {'platform': 'ethereum', 'address': '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'},
    ],
    'USDC': [
        {'platform': 'ethereum', 'address': '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48'},
        {'platform': 'solana', 'address': 'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'},
        {'platform': 'solana', 'address': '0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359'},
        {'platform': 'polygon', 'address': '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359'},
        {'platform': 'polygon', 'address': '0x2791bca1f2de4661ed88a30c99a7a9449aa84174'},
        {'platform': 'arbitrum-one', 'address': '0xaf88d065e77c8cc2239327c5edb3a432268e5831'},
    ],
    'USDG': [
        {'platform': 'ethereum', 'address': '0xe343167631d89b6ffc58b88d6b7fb0228795491d'},
    ],
    'USDR': [
        {'platform': 'ethereum', 'address': '0x7b43e3875440b44613dc3bc08e7763e6da63c8f8'},
    ],
    'USDT': [
        {'platform': 'ethereum', 'address': '0xdac17f958d2ee523a2206206994597c13d831ec7'},
        {'platform': 'tron', 'address': 'USDT_TRON'},
        {'platform': 'polygon', 'address': '0xc2132d05d31c914a87c6611c10748aeb04b58e8f'},
        {'platform': 'arbitrum-one', 'address': '0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9'},
    ],
    'USELESS': [
        {'platform': 'solana', 'address': 'Dz9mQ9NzkBcCsuGPFJ3r1bS4wgqKMHBPiVuniW8Mbonk'},
    ],
    'USUAL': [
        {'platform': 'ethereum', 'address': '0xc4441c2be5d8fa8126822b9929ca0b81ea0de38e'},
    ],
    'VANRY': [
        {'platform': 'ethereum', 'address': '0x8de5b80a0c1b02fe4976851d030b36122dbb8624'},
    ],
    'VELODROME': [
        {'platform': 'optimism', 'address': '0x9560e827af36c94d2ac33a39bce1fe78631088db'},
    ],
    'VINE': [
        {'platform': 'solana', 'address': '6AJcP7wuLwmRYLBNbi825wgguaPsWzPBEHcHndpRpump'},
    ],
    'VIRTUAL': [
        {'platform': 'solana', 'address': '3iQL8BFS2vE7mww4ehAqQHAsbmRNCrPxizWAT2Zfyr9y'},
    ],
    'VSN': [
        {'platform': 'ethereum', 'address': '0x699ccf919c1dfdfa4c374292f42cadc9899bf753'},
    ],
    'VVV': [
        {'platform': 'base', 'address': '0xacfe6019ed1a7dc6f7b508c02d1b04ec88cc21bf'},
    ],
    'W': [
        {'platform': 'solana', 'address': '85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ'},
    ],
    'WAXL': [
        {'platform': 'ethereum', 'address': '0x467719ad09025fcc6cf6f8311755809d45a5e5f3'},
    ],
    'WBTC': [
        {'platform': 'ethereum', 'address': '0x2260fac5e5542a773aa44fbcfedf7c193bc2c599'},
    ],
    'WELL': [
        {'platform': 'base', 'address': '0xa88594d404727625a9437c3f886c7643872296ae'},
    ],
    'WEN': [
        {'platform': 'solana', 'address': 'WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk'},
    ],
    'WIF': [
        {'platform': 'solana', 'address': 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm'},
    ],
    'WLD': [
        {'platform': 'optimism', 'address': '0xdc6ff44d5d932cbd77b52e5612ba0529dc6226f1'},
    ],
    'WLFI': [
        {'platform': 'ethereum', 'address': '0xda5e1988097297dcdc1f90d4dfe7909e847cbef6'},
    ],
    'WOO': [
        {'platform': 'ethereum', 'address': '0x4691937a7508860f876c9c0a2a617e7d9e945d4b'},
    ],
    'XCN': [
        {'platform': 'ethereum', 'address': '0xa2cd3d43c775978a96bdbf12d733d5a1ed94fb18'},
    ],
    'XNY': [
        {'platform': 'bsc', 'address': '0xe3225e11cab122f1a126a28997788e5230838ab9'},
    ],
    'YFI': [
        {'platform': 'ethereum', 'address': '0x0bc529c00c6401aef6d220be8c6ea1667f6ad93e'},
    ],
    'YGG': [
        {'platform': 'ethereum', 'address': '0x25f8087ead173b73d6e8b84329989a8eea16cf73'},
    ],
    'ZEREBRO': [
        {'platform': 'solana', 'address': '8x5VqbHA8D7NkD52uNuS5nnt3PwA8pLD34ymskeSo2Wn'},
    ],
    'ZETA': [
        {'platform': 'ethereum', 'address': '0xf091867ec603a6628ed83d274e835539d82e9cc8'},
    ],
    'ZEUS': [
        {'platform': 'solana', 'address': 'ZEUS1aR7aX8DFFJf5QjWj2ftDDdNTroMNGo8YoQm3Gq'},
    ],
    'ZEX': [
        {'platform': 'solana', 'address': 'ZEXy1pqteRu3n13kdyh4LwPQknkFk3GzmMYMuNadWPo'},
    ],
    'ZORA': [
        {'platform': 'base', 'address': '0x1111111111166b7fe7bd91427724b487980afc69'},
    ],
    'ZRO': [
        {'platform': 'ethereum', 'address': '0x6985884c4392d348587b19cb9eaaf157f13271cd'},
    ],
    'ZRX': [
        {'platform': 'ethereum', 'address': '0xe41d2489571d322189246dafa5ebde1f4699f498'},
    ],
}
