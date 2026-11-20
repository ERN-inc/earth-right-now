# GDE Weekly Audit — 2026-11-20 (JST)

## Scope and evidence
Reviewed `GDE_ROADMAP.md`, `GDE_ACCESS_AUDIT.md`, recent repository commits, `live.json`, RSS, sitemap, embed and homepage, plus EARTH BREAK pilot commit. Audit interval: 2026-11-14 through 2026-11-20.

**Traffic outcome:** GA4 sessions, Search Console impressions/clicks, country-level visits, referrers and outbound YouTube event counts were not available through the GitHub repository or connected reporting tools in this audit. Do not treat them as zero or infer growth from commits. A web search showed the ERN homepage indexed in one search result, but this does not establish Google indexing of all pages or any traffic.

## Verified repository observations
- XML sitemap lists 22 URLs: homepage, embed guide, 3 localized landings (ja/es/id), 4 topic guides, city hub and 12 city guides.
- RSS exists and currently describes an offline broadcast.
- `embed.html` checks `live.json` and provides an offline fallback.
- `live.json` says offline and `checkedAt=2026-11-17T09:38:53Z`; this is **over three days old** as of this audit. It does **not** prove that the live stream is actually offline now.
- The latest repository commit prior to this audit was 2026-11-17. No subsequent status refresh was visible.
- EARTH BREAK pilot draft was committed 2026-11-16 at `distribution/EARTH_BREAK_PILOT.md`; includes three drafts, homepage-first UTM links and publishing gate. No external publishing evidence.
- Existing GDE health workflow only checked that endpoints responded and, when status was live, that the ID appeared in HTML/RSS. It did not check freshness of the detector.
- Homepage retains an older YouTube thumbnail ID while status is offline; do not label this the current broadcast. Metadata drift remains a risk.
- Public endpoint HTTP verification and current Actions-run status were **not independently confirmed** in this run (web fetch unavailable and connector lacks general workflow-run listing). A prior successful run does not establish current health.

## P0 / 48-hour gate
**Not verified complete.** RSS and discovery artifacts exist, but live status freshness is failing by repository timestamp; current Actions/Pages run status and GA4/GSC reporting cannot be confirmed. Priority: restore detector schedule and verify published pages, then obtain real acquisition baselines.

## EARTH BREAK / 72-hour gate
**Creative and UTM draft preparation complete in repository, publication not verified.** External posting requires approval and approved account access. No observed referral sessions are available.

## Corrective action this audit
Updated `.github/workflows/gde-health.yml` to fail when `live.json` checkedAt is more than 3 hours old, and to parse RSS XML in both live and offline cases. This converts silent detector staleness into an explicit CI failure. Commits: `e45e198b`, `977f61ea`. GitHub write confirmed; actual workflow execution remains unverified.

## Next highest-impact work, in order
1. Diagnose why the detector stopped refreshing after 2026-11-17: GitHub Actions enablement, schedule, failures, permissions and YouTube detection; repair only after observing root cause. Check actual stream state independently.
2. Retrieve Search Console last 7 vs preceding 7 days: clicks, impressions, queries, pages, countries. Retrieve GA4 sessions by source/medium, landing page, country, and YouTube outbound events. Decide which entry pages deserve investment.
3. Verify public HTTP and deploy status for homepage, embed, feed, sitemap, three languages and key city guides; fix actual failures.
4. If approved, launch one authentic EARTH BREAK pilot on an already connected platform, landing on the official site; measure referral sessions before scaling.
5. Improve existing high-intent ambient/screensaver content based on measured search queries; do not mass-generate thin pages or spend cycles on low-impact UI polish.

## Decision boundaries
No paid services, spam, fake engagement, desktop-app changes, unapproved external posting or unsupported claims of traffic gains.
