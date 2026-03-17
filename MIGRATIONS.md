# Known Token Migrations

This file documents token migrations that were detected (or missed) by the monitor,
serving as a reference for improving detection coverage.

---

## MANTRA: OM → MANTRA (March 2026)

**Source:** https://support.kraken.com/articles/mantra-om-migration
**Announced:** February 18, 2026
**Detection status:** ⚠️ MISSED — announced via Kraken Support Center, not the blog feed

### Summary

MANTRA ($OM) migrated and rebranded to MANTRA ($MANTRA).
Conversion rate: **1 OM : 4 MANTRA** (performed automatically on Kraken).

### Key dates

| Date | Event |
|------|-------|
| Feb 24, 14:00 UTC | OM margin pairs set to reduce-only |
| Feb 25, 14:00 UTC | OM deposits/withdrawals paused; margin positions closed and delisted |
| Feb 26, 14:00 UTC | OM spot markets in cancel-only mode |
| Feb 27, 14:00 UTC | All open OM spot orders cancelled |
| Mar 2, 14:00 UTC  | OM spot markets delisted |
| Mar 3, by 23:59 UTC | MANTRA deposits/withdrawals open; spot markets listed in post-only mode |
| Mar 4, 14:00 UTC  | MANTRA spot and margin markets fully open |

### Why it was missed

The monitor only tracked `https://blog.kraken.com/feed`.
Kraken publishes token migration and delisting notices in their **Support Center**
(`support.kraken.com/articles/...`), not on the blog.

**Fix applied:** Added `KrakenSupport` feed entry in `config.py`:
```
"KrakenSupport": "https://support.kraken.com/hc/en-us/categories/200187583-Announcements/articles.rss"
```

### Tokens involved

- `OM` (old symbol — already in `TOKENS` list)
- `MANTRA` (new symbol — already in `TOKENS` list)
- Keywords matched: `migration`, `rebrand`, `delist`, `swap`
