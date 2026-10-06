# Demo: ccfddl-query · open CCF-A venues for computer vision (2026-10-06)

- **Agent**: Claude Code, live upstream data (not the fixture). A demo run, not a user request.
- **Input**: "CV 方向 CCF-A 现在还能投什么？"
- **What ran**: `list --domain cv --ccf-rank A --status open --within-days 180 --format json`, then `refresh-cache`, then the same `list` again.
- **Output**: summary below; the raw JSON stays local.

As of 2026-10-05 23:01 UTC, after refreshing from `https://ccfddl.github.io/conference/allconf.yml` (2301 entries):

| Conference | CCF / CORE / THCPL | ccfddl category | Deadline | Date | Place |
|---|---|---|---|---|---|
| WWW 2027 | A / A* / A | MX | 2026-10-25 23:59:59 AoE | May 10-14, 2027 | Dublin, Ireland |
| CVPR 2027 | A / A* / A | AI | 2026-11-16 23:59:00 UTC-12 | June 20-25, 2027 | Seattle, WA, United States |
| ACL 2027 | A / A* / A | AI | 2027-01-04 23:59:59 UTC-12 | August 17-22, 2027 | Kyoto, Japan |

`cv` is a convenience preset mapped to ccfddl categories AI, CG and MX, so non-vision venues (WWW, ACL) appear; the script reports the mapping in `notes`.

## What this run showed
- **A stale cache gave a wrong answer first.** The first `list` read a local cache written on 2026-07-15 and returned one venue, WWW 2027 with a 2026-10-18 deadline. The only hint was the note `cache data was used`; the cache age was not shown. After `refresh-cache` the same query returned the three rows above, with WWW at 2026-10-25.
- Until the script reports cache age, run `refresh-cache` before a recommendation-style query.
