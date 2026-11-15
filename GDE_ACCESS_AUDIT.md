# ERN GDE Access Growth Audit

Date: 2026-11-14
Scope: Public acquisition/distribution surfaces for `ERN-inc/earth-right-now`.
Goal: Identify concrete reasons traffic is not growing and convert findings into measurable, automatable fixes.

## Executive finding

The current site is technically crawlable, but its acquisition surface is still extremely small. The main public site is essentially one indexable landing page, with one URL in the sitemap, no multilingual landing pages, no city-specific discovery pages, and only limited external distribution surfaces. That makes meaningful organic search growth unlikely even if the homepage itself is technically healthy.

A second problem was detected: the homepage still contained stale hard-coded YouTube video references while `live.json` and structured data pointed to the current broadcast. This can produce inconsistent user/social-preview behavior and is now being corrected.

A third problem is measurement depth. Google Analytics was already installed, but key distribution actions were not explicitly measured, making it harder to identify where the growth funnel fails. Share/copy/fullscreen/outbound-YouTube events are now instrumented.

## Evidence observed

### 1. Search footprint is tiny
- `sitemap.xml` contains only the homepage.
- `sitemap-ern.xml` contains only the homepage.
- There are no multilingual landing pages yet.
- There are no city discovery pages yet.
- There are no useful indexable topic pages such as sunrise/sunset/screensaver guides yet.

Impact: there are very few search queries for which Google can rank a relevant ERN page.

### 2. Exact-brand discovery is weak
A fresh web search for the GitHub Pages URL / brand did not surface the GitHub Pages site prominently; another unrelated "Earth Right Now" domain appeared instead.

Impact: even brand searches may leak attention to other properties. ERN needs stronger entity consistency, external references, structured entity data, and more distinct useful landing pages.

### 3. Live metadata drift existed
Observed before this audit:
- `live.json`: current live video `BmgRaSxWcpU`
- VideoObject structured data: `BmgRaSxWcpU`
- Homepage iframe/default/share URLs still contained old ID `hg8IooPYXeY`

Impact: homepage playback fallback, outbound YouTube links and social preview image could lag the current broadcast.

Action: corrected hard-coded references and added health-check assertions so this drift is detected automatically.

### 4. Distribution actions were under-measured
Google Analytics tag already exists, but explicit events for:
- Share Earth
- Copy Website Link
- Full Screen
- outbound YouTube clicks

were missing.

Impact: raw visits alone do not show whether visitors engage, share, or leave for YouTube.

Action: these events are now instrumented with the existing zero-cost GA setup.

### 5. External distribution is still early
Current automated surfaces include:
- homepage
- live status JSON
- RSS
- embeddable player
- machine-readable distribution endpoints
- Product Hunt listing
- YouTube live presence

But the system does not yet have broad multilingual, city, publisher, social, or partner surfaces.

Impact: no technical mechanism can produce billion-scale reach from a single landing page alone.

## Ranked causes of slow growth

1. **Insufficient discovery inventory** — too few indexable useful pages.
2. **Weak external distribution/backlink footprint** — few independent sites currently point users/search engines to ERN.
3. **No multilingual search inventory yet** — global audience is limited by English-only discovery.
4. **No city-level intent capture yet** — ERN covers 286 cities but search has no dedicated city entry points.
5. **Insufficient share-loop instrumentation** — now partially fixed.
6. **Metadata consistency drift** — stale live references detected and now guarded.
7. **No proven repeatable social acquisition loop yet** — future phase.

## Immediate remediation plan

### P0 — Reliability and measurement
- Keep live ID synchronized across homepage, VideoObject, OG/Twitter preview, RSS and live.json.
- Fail GDE health checks when homepage/feed are stale.
- Measure share/copy/fullscreen/outbound actions.
- Verify public deploy and Actions success before calling complete.

### P1 — Discovery inventory
- Build SEO-safe multilingual landing pages.
- Build useful city discovery pages in cohorts.
- Add unique topic/intent pages only where content is genuinely useful.
- Expand sitemap generation automatically.

### P2 — Distribution
- Publish one-snippet embed instructions.
- Create stable machine-readable endpoints.
- Add compliant publisher/share assets.
- Use approved APIs for connected social platforms only.

### P3 — Growth measurement
Track:
- users / sessions
- source / medium
- landing page
- country
- share events
- copy-link events
- outbound YouTube clicks
- returning users
- city/language landing performance once deployed

## Validation rules

Do not call traffic-growth work successful based on deployment alone. Success requires evidence of:
- more indexed useful landing pages,
- rising impressions/clicks from search,
- more referral domains,
- increasing real-user sessions,
- measurable share/outbound engagement,
- no stale live metadata.

## Current conclusion

The main issue is not that the site is blocked from crawling. The larger issue is that ERN currently has too little searchable/distributable surface area to create sustained organic growth. The next highest-leverage work is to multiply useful entry points (languages + cities) while preserving technical quality and measuring whether those entry points actually produce human traffic.


## 2026-11-15 daily verification — new root-cause finding

**Confirmed code defect (P0):** The live SEO synchronization script used doubled backslashes inside Python raw regex patterns. These patterns could not match the actual `<script type="application/ld+json">` tag and YouTube metadata URLs correctly. The code also wrote a literal backslash-n to `sitemap.txt`, instead of a newline. This is a concrete explanation for why metadata drift could persist even though the GitHub Actions workflow was configured to run periodically.

**Changes committed:** Corrected regex escaping and substitution callbacks in `scripts/update_seo.py`; added isolated live/offline/idempotence regression tests; configured the scheduled live workflow to run the tests before detector/SEO writes.

**Verification boundary:** GitHub content writes succeeded. GitHub Actions run conclusion and public GitHub Pages HTTP status could not be independently verified in this run. No claim of successful production deploy or traffic lift is made.

**Next checks:** Confirm the Actions test step passes; confirm public `live.json`, VideoObject, OG/Twitter previews, no-JS iframe, RSS and all sitemap variants are synchronized after the next successful run. Compare GA4 acquisition reports and Search Console impressions to distinguish indexing, discovery, click-through and retention bottlenecks. Do not infer actual traffic numbers without access to those reports.

## 2026-11-15 regression gate repair

**Confirmed blocker:** The scheduled GitHub Actions workflow runs `tests/test_update_seo.py` before synchronizing metadata. The test still asserted that `sitemap.txt` contained only the homepage URL, even though the live SEO script now deliberately writes all discovery URLs. Consequently, the test was guaranteed to fail after discovery expansion and could prevent scheduled live updates.

**Repair:** Updated the regression test to assert the complete `DISCOVERY_URLS` text sitemap and presence of each URL in both XML sitemap variants. Commit `d2e807f457a77ab85dd46057903fe2dfede37515`. The script and test now express the same sitemap contract.

**Verification boundary:** GitHub write succeeded; the remote Actions result and public Pages endpoints remain unverified because public HTTP access was unavailable from this execution environment. Do not claim a passing workflow or public deployment until observed.
