---
name: seo-aeo-pass
description: Full SEO and AEO (AI answer visibility) pass for any website, from free first-party data. Measures Search Console, analytics and AI answers, audits the site technically and for AI crawlers, finds keywords by buyer value instead of volume, checks each against the live results, and ends in a ranked plan, page drafts and a report. Runs as a multi-agent workflow (better) or a flat single-agent pass. Use for SEO audits, keyword research, "why don't we rank", content plans, competitor gaps, getting cited in ChatGPT / Perplexity / Gemini / Claude / Google AI Overviews, GEO, LLM visibility, AI crawler checks, or triaging a pasted audit or keyword list from another tool. Paid keyword, backlink and AI-visibility tools are used only when connected.
license: MIT
compatibility: Python 3.9+ (standard library only) and network access. Works best with a Google Search Console MCP and a GA4 or Matomo MCP. The multi-agent mode uses Claude Code's Workflow tool when present and falls back to subagents or a flat pass elsewhere.
metadata:
  author: Simon Gloel
  version: "1.0.0"
  repository: https://github.com/simongloel/seo-aeo-pass
---

# SEO and AEO pass

One pass that ends with a reading of what holds the site back, a keyword list where every term has a reason, a ranked plan, optional page drafts and a report on disk. It works without any paid tool. Paid tools add numbers; the decisions below don't depend on them.

Three rules apply to every step:

1. **Never invent a number.** Search volume, difficulty, traffic and authority from tools are model estimates (`references/metrics.md` explains how each vendor computes them). Label every figure with its source and date, or call it a signal. Never print autocomplete counts or relative scores as volumes or money.
2. **Pick terms by what a visitor is worth, not by volume.** A few visitors who fit the offer beat many who don't (`references/keywords.md`).
3. **Read-only on everything live.** No writes to Search Console, analytics, keyword tools or the site without the user's yes. Paid API calls only within the budget agreed at intake.

## Step 0: intake

Ask these in one round (use the AskUserQuestion tool where the client has one, otherwise ask in chat). Skip what the user already said.

1. **Mode.** Offer exactly these two:
   - **Multi-agent workflow (recommended).** Six measurement streams run in parallel, every keyword cluster is researched and then attacked by a skeptic agent, a critic checks the plan. Better results, uses several times the tokens and takes longer.
   - **Flat analysis.** One agent works through the same steps in sequence with less depth: fewer clusters, no skeptic pass, no critic. Cheaper and faster, noticeably weaker output.
2. **Site and markets**: URL, sitemap if not at `/sitemap.xml`, countries and languages that matter.
3. **What makes money**: what the site sells, what counts as a conversion, a rough value per conversion if known. Without it, scoring falls back to CPC.
4. **Competitors** they know of (optional; the pass finds the search competitors anyway).
5. **Output**: analysis and plan only, or also drafts of the top pages. Building pages in their codebase comes later, after they have seen the plan.
6. **Spend**: may the pass spend money on API calls (AI visibility runs via provider keys, paid keyword tools)? If yes, a cap.

Then check which data sources answer (`references/data-sources.md`): try the Search Console MCP (list sites), the analytics MCP (GA4 or Matomo), Bing Webmaster, and any keyword or AI-visibility tool. Say which are missing. If Search Console or analytics is missing, recommend connecting them before running, with the install command from `references/data-sources.md`. They are the two connectors that change the result most: real impressions and positions, and which entry pages convert. Proceed without them if the user prefers, and list the gap in the report.

Create the output folder outside the user's code repository: `~/seo-reports/<YYYY-MM-DD>-<site>/` unless the user names another place. If you run as a subagent and writing files is refused, return file contents in your answer and let the parent write them.

## Step 1a: multi-agent workflow mode

If the Workflow tool is available, run the bundled script, passing the intake as `args`. The user's choice of this mode in step 0 is their opt-in to the workflow.

```
Workflow({
  scriptPath: "<this skill's folder>/workflows/seo-aeo-pass.js",
  args: {
    site: "https://example.com", sitemap: "https://example.com/sitemap.xml",
    markets: [{country: "de", lang: "de"}, {country: "us", lang: "en"}],
    business: "<what is sold, what a conversion is, value>", converts: "<how: trial, demo request, purchase>",
    competitors: ["a.com", "b.com"], connectors: {gsc: true, analytics: "matomo", keywordTool: false, aiVisibilityTool: false},
    logs: "<path to access logs or omit>", outDir: "<absolute output folder>", skillDir: "<absolute path of this skill>",
    mode: "analyze" | "draft", maxClusters: 8, maxDrafts: 5, date: "<today>", spend: "<cap or none>"
  }
})
```

Phases: Measure (six parallel streams: search data, technical, claims, authority and competitors, AI visibility, business value) -> Diagnose -> Keywords (per cluster: expand, check live results, score; then a skeptic tries to kill each term) -> Plan (plus a completeness critic) -> Draft (optional) -> Report.

If the Workflow tool is not available but subagents are (Claude Code without workflows, other agent hosts), run the same phases yourself: start the six measurement streams as parallel subagents with the prompts from the script, then do Diagnose, run one subagent per cluster followed by a skeptic subagent, then Plan and the critic. Without subagents, use the flat mode and tell the user why.

When the workflow returns, make sure `report.md` exists (if the report agent could not write it, the workflow returns the report text; write it yourself), check two or three of its claims against the data, and go to step 3.

## Step 1b: flat mode

Same steps, in order, with less depth. Keep the raw numbers for the report.

1. **Search data.** Search Console, last 28 days and the 28 before, for each market, by query, page and country: clicks, impressions, CTR, position, brand share, non-brand queries on page one, striking distance (positions 4-30 with impressions and low CTR), queries with no page aimed at them, pages losing clicks. Read "Reading Search Console correctly" in `references/data-sources.md` first (country codes, lag, row sorting, subdomains, anonymised queries).
   **Who converts.** With an analytics MCP: organic entry pages, AI-assistant referrals, conversions by entry page, country and language. Without one: the Matomo Reporting API or GA4 Data API with a token, the product's own database or payment provider (read-only), or ask the user for an export. If none is possible, say so in the report and score by CPC; don't skip this silently, it decides the keyword list.
2. **Technical.** `python3 scripts/site_audit.py <sitemap> --out <out>/audit.json` and `python3 scripts/ai_readiness.py <site> --pages <a few key paths>`. Sort findings with `references/technical.md`.
3. **Claims.** Read pricing, plans, home and comparison pages; check every claim a buyer relies on against the live product. The fastest source of truth is the product's own: a pricing or plans API or MCP, the plan configuration in the code, the checkout page.
4. **Authority.** `python3 scripts/authority.py <site> <competitors>`, plus a backlink tool if connected. Decide whether the site has an authority problem.
5. **AI answers.** Write 10-15 buyer prompts. Use an AI-visibility tracking tool if one is connected, and pull both overall and unbranded share of voice. Else `scripts/ai_visibility.py` if a provider key is set and spend is allowed. Else give the user the prompt list to try in ChatGPT, Perplexity and Gemini, or use a browser tool if one is connected. A web search tool is not an AI assistant and does not measure this. See `references/aeo.md`.
6. **Keywords.** Seeds from the offer, `scripts/keyword_suggest.py`, Search Console patterns, two competitor sitemaps; one batch through a keyword tool if connected; live results for the 10-15 best; `scripts/serp_difficulty.py` and `scripts/keyword_score.py`. Filter with `references/keywords.md`. Note what your search tool cannot show: many web search tools are fixed to one country and show neither ads nor AI Overviews, so say "SERP features not seen" and which locale you checked.
7. **Plan and report** as in step 2.

## Step 2: the reading, the plan, the report

State the reading in three to five sentences first: what holds the site back most and what follows (`references/playbook.md` has the common readings). Then the plan: at most 25 actions, ranked by value per effort in the order the playbook gives, each with its evidence and effort, owner decisions marked. Write the report with `references/report-template.md`. It must include the left-out terms with reasons and a "Not measured" section listing every missing source.

Show the user the reading, the top ten actions and the report path. Don't paste the whole report into chat.

## Step 3: building pages (only after the user agrees)

When the user wants pages built in their site:

- Work in a branch or worktree, never on their main branch directly.
- Follow `references/content.md`: page type matched to what ranks, every claim verified, answer first, "when this is the wrong choice", the exact term in title and H1, questions as headings, links in from crawled pages.
- Load a writing-style skill if one is installed (for example `human-writing`).
- Before shipping, run the site's build and tests, re-run `site_audit.py` on the result, and check titles, canonicals and hreflang in the built HTML.
- After deploy, verify live per `references/technical.md` (200s, sitemap, IndexNow answer, "Request indexing" for the two or three most important URLs, a look at desktop and phone width).
- Pace: on a domain with little authority, fewer pages linked from pages Google already crawls beat many pages at once.

## Step 4: re-read

Put two re-read dates in the report (two and four weeks out): positions, impressions and clicks for the target URLs, indexing state, AI mention rate on the same frozen prompt set, conversions by entry page. On the re-read, compare and say plainly what moved and what didn't. Pages that drew visitors who never converted are a finding too.

## Triage of pasted tool output

When the user pastes a site audit tool's issues, its suggested actions, a keyword tool's plan or a consultant's checklist: go through every item, answer done / doing / not doing with the reason, using the fix / fix-when-cheap / leave groups in `references/technical.md` and the keyword filter for content suggestions. Nothing skipped silently.

## What this skill does not do

It doesn't buy links, invent reviews, ratings, authors, customers or statistics, cloak content for bots, post on forums or submit to directories on the user's behalf, or write pages for terms the business can't serve. Outreach is prepared; sending it is the user's step.

## Files

- `references/metrics.md`: how commercial SEO and AI-visibility tools compute volume, difficulty, authority, traffic, CTR and AI visibility, and how to approximate each from free data. Read before quoting or estimating any metric.
- `references/keywords.md`: buyer-value keyword method, filter, traps.
- `references/technical.md`: what to fix, what to leave, live verification.
- `references/content.md`: page types and what makes a page rank and get cited.
- `references/aeo.md`: AI answer visibility: what decides it, how to measure, what to do per gap.
- `references/playbook.md`: readings, order of work, links, measurement traps, field notes.
- `references/data-sources.md`: MCP connectors with install commands, how to use paid tools sparingly, free stand-ins.
- `references/report-template.md`: report structure.
- `scripts/`: `keyword_suggest.py`, `keyword_score.py`, `serp_difficulty.py`, `site_audit.py`, `ai_readiness.py`, `ai_visibility.py`, `ai_crawler_logs.py`, `authority.py`. Each prints its usage with `--help`. Standard library only.
- `workflows/seo-aeo-pass.js`: the multi-agent workflow for Claude Code.
