# ERN GLOBAL DISTRIBUTION ENGINE (GDE) — ROADMAP

Start date: 2026-11-14
Goal: Build a zero-extra-cost, policy-compliant, fully automated global distribution system for EARTH RIGHT NOW (ERN).

## Non-negotiable rules
- Do not modify the ERN desktop application.
- Zero additional paid services or paid APIs unless explicitly approved later.
- No spam, unsolicited bulk messaging, deceptive redirects, forced browsing, fake engagement, bot traffic, or platform-rule evasion.
- Do not call unfinished or unverified work complete.
- Prefer reversible, low-risk changes.
- Preserve the existing ERN website visual design unless a change is required for distribution functionality.
- Keep all automation auditable in GitHub.

## Phase 1 — Distribution foundation (2026-11-14 to 2026-11-17)
- Keep live YouTube ID detection and SEO metadata synchronized.
- Keep sitemap variants and RSS feed synchronized.
- Maintain embeddable live player.
- Add machine-readable distribution metadata where useful.
- Add health checks for public endpoints and GitHub Actions.
- Verify GitHub Pages deploys after each distribution change.

Exit criteria:
- Live ID, structured data, feed, sitemap, embed endpoint all update automatically.
- Latest GitHub Actions run succeeds.
- Public endpoints are reachable.

## Phase 2 — Shareability & referral loop (2026-11-18 to 2026-11-20)
- Strengthen share metadata and canonical links.
- Add non-intrusive copy/share/embed helpers without redesigning the site.
- Add UTM-compatible sharing links while preserving canonical URL.
- Add basic referral measurement using existing analytics only.
- Add lightweight embed documentation for third-party sites.

Exit criteria:
- Visitors can share/embed ERN with minimal friction.
- Share previews use the current live stream.
- No paid service is required.

## Phase 3 — Multilingual discovery (2026-11-21 to 2026-11-27)
- Add SEO-safe multilingual landing content or language endpoints for major world languages.
- Start with English, Japanese, Spanish, Portuguese, French, German, Indonesian, Hindi, Arabic, Korean, Chinese.
- Use hreflang/canonical rules correctly.
- Avoid thin or duplicate-content pages.
- Extend sitemap generation automatically.

Exit criteria:
- Major-language discovery pages are indexable and automatically maintained.
- Sitemap and metadata remain valid.

## Phase 4 — City discovery network (2026-11-28 to 2026-12-07)
- Build indexable city-discovery pages or data-driven routes for ERN cities without changing the desktop app.
- Prioritize high-population and globally searched cities first.
- Each page must have useful unique context, not keyword stuffing.
- Link back to the live Earth experience.

Exit criteria:
- First city cohort is publicly reachable, internally linked, and in sitemap.
- Generation/update process is automated.

## Phase 5 — External distribution surfaces (2026-12-08 to 2026-12-17)
- Prepare standards-compliant feeds and embed assets for blogs, schools, hotels, media sites, dashboards and directories.
- Create reusable embed snippets and attribution text.
- Surface Product Hunt, GitHub and YouTube consistently.
- Where a connected platform provides an approved API, automate compliant publishing.

Exit criteria:
- External publishers can embed ERN with one snippet.
- Distribution assets remain synchronized automatically.

## Phase 6 — Organic social content pipeline (2026-12-18 to 2026-12-30)
- Generate reusable text/caption packages from verified ERN events.
- Prepare per-platform variants for YouTube, X, Instagram, Threads, TikTok, Facebook, Reddit where policy-compliant.
- Automate posting only through officially connected/approved APIs.
- Never mass-DM, auto-reply spam, or fabricate engagement.

Exit criteria:
- Content packages are generated automatically.
- Connected platforms can publish through approved integrations.

## Phase 7 — Measurement & optimization (2026-12-31 onward)
- Track public traffic, referral sources, search visibility, embed usage and content performance using available zero-cost analytics.
- Prioritize channels that generate real human visits.
- Retire low-value automation.
- Keep daily execution and weekly audit reports.

## Daily execution rule
Each daily automation run must:
1. Read this roadmap and current repository state.
2. Determine the current phase by date and incomplete exit criteria.
3. Inspect latest GitHub Actions and public distribution files.
4. Execute as many safe, reversible, zero-cost tasks as can be completed and verified in the run without requiring new user credentials or consent; do not artificially limit the run to one task.
5. Verify the change.
6. Report exactly what changed, what was verified, and what remains.
7. If blocked by a credential/permission/manual platform action, report the smallest required user action instead of guessing.

## Weekly audit rule
Once per week:
- Compare progress against exit criteria.
- Check failures, stale metadata, broken public links, duplicate/low-quality SEO risks and automation drift.
- Reprioritize the next seven days.
- Never inflate completion status.
