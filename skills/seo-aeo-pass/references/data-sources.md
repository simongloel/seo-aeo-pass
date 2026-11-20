# Data sources and connectors

Check which of these answer before planning the pass, and tell the user which are missing. A pass with Search Console and analytics is worth several without them.

## Recommended connectors (free)

| Data | MCP server | Install | Auth |
|---|---|---|---|
| Google Search Console | AminForou/mcp-gsc (PyPI `mcp-search-console`). Google has no official server. | `claude mcp add gsc -e GSC_OAUTH_CLIENT_SECRETS_FILE=/abs/path/client_secrets.json -- uvx mcp-search-console` | Your own Google Cloud OAuth desktop client (read-only by default), or a service account added as a user on the property. Writes need `GSC_ALLOW_DESTRUCTIVE=true`; leave it off. |
| Google Analytics 4 | googleanalytics/google-analytics-mcp (official) | `claude mcp add analytics-mcp --scope user -e GOOGLE_APPLICATION_CREDENTIALS=<adc.json> -e GOOGLE_CLOUD_PROJECT=<project> -- pipx run analytics-mcp` | `gcloud auth application-default login --scopes https://www.googleapis.com/auth/analytics.readonly,https://www.googleapis.com/auth/cloud-platform`; enable the Analytics Admin and Data APIs. |
| Matomo | Official Matomo MCP (since May 2026): built into Matomo Cloud; self-hosted needs the McpServer plugin | Superuser enables it, copies the endpoint URL into the client. Guide: https://matomo.org/faq/how-to/how-to-configure-the-matomo-mcp-server/ | Matomo token or OAuth. Without MCP, the Reporting API works with a `token_auth` over plain HTTP. |
| Bing Webmaster Tools | community: `mcp-server-bwt` (PyPI) or `@isiahw1/mcp-server-bing-webmaster` (npm). Vet before use. | uvx / npx | API key from Bing Webmaster > Settings > API access. Bing also gives free backlinks and keyword research, and since 2026 an "AI Performance" report for Copilot citations. |
| PageSpeed / CrUX | no official server; call the APIs directly | `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<url>&strategy=mobile` and `https://chromeuxreport.googleapis.com/v1/records:queryRecord?key=<key>` | Free Google API key. |

Pin exact versions when you put any `uvx`/`npx` launcher into a shared config.

## Reading Search Console correctly

- **Country filters use ISO 3166 alpha-3** codes: DEU, USA, GBR, AUT, CHE, FRA. Not "de" or "us".
- **Data lags 2-3 days.** "Last 28 days" should end three days ago, and compare with the 28 days before that.
- **Rows come back sorted by clicks** and capped by the row limit. Terms at positions 5-20 with impressions but no clicks drop off the end. Use a quick-wins or striking-distance tool if the MCP has one (mcp-gsc and others do), or pull with a high row limit and filter by position yourself.
- **Domain properties (`sc-domain:`) include every subdomain.** App, docs, status or customer subdomains show up in page rows and distort totals. Filter pages to the marketing host.
- **Anonymised queries** (rare or personal) are left out of query rows but counted in totals. Brand share = clicks on brand queries / total clicks is therefore a lower bound; say so.
- **Impressions are a floor for demand**: the site is not shown for every search of the term, least of all at low positions.
- **Access can vanish silently** (unverified owner, removed service account). Confirm the property answers at the start.
- Sitemap reports show an "indexed" count that is often 0 and means nothing; use URL inspection for single pages.
- Writing actions (submit sitemap, request indexing) usually need more rights than read access; they are the owner's step.

## Optional paid connectors

Use them to rank and enrich a candidate list the free sources produced, in batches. Never let a paid tool generate the list alone: its volumes are models (see `metrics.md`), and its keyword ideas skew to what everyone else targets.

Any keyword suite, backlink tool, SERP API or AI-visibility tracker with an MCP server or API works. Check which one is connected and read its own docs for report names and costs.

Habits that save money and units:

- Batch: one report for 30-50 terms, never one call per term. Prefer the cheapest report that answers the question; per-row reports get expensive fast.
- Always set a row limit. Ask only for the columns you use.
- To see which terms carry volume in a market, take a big competitor's folder (e.g. `/de/`) filtered to positions 1-10 instead of broad keyword expansion.
- A "no data" answer is final; don't retry it.
- When several agents share one paid account, give each a budget. Parallel agents can drain a shared pool in an afternoon.
- Reports that only exist in the tool's web interface (suggested actions, AI-visibility dashboards) can't be read through the API; ask the user to paste them.
- AI-visibility trackers: start with the project list, pull overall and unbranded numbers, and check when the project's data begins (see `aeo.md`).

## Always available, no account

| Need | Source |
|---|---|
| What people type | `scripts/keyword_suggest.py` (Google + Bing autocomplete) |
| Who ranks, what kind of page, AI Overview or not | WebSearch, or a SERP API; for exact Google layout, look in a browser |
| What competitors found worth a page | their `sitemap.xml` (grep for pricing, alternative, vs, compare, for-, integrations) |
| Authority comparison | `scripts/authority.py` (Tranco, Open PageRank, Common Crawl) |
| Technical state | `scripts/site_audit.py`, `scripts/ai_readiness.py` |
| AI crawlers and AI referrals | `scripts/ai_crawler_logs.py` on server logs |
| AI answer visibility | `scripts/ai_visibility.py` with any of the four provider API keys |
| Topic interest over time | Google Trends (relative), Wikipedia pageviews API |
| Real wording and pain | Reddit and Hacker News search (`hn.algolia.com/api/v1/search?query=`) |

## Standing in for the numbers a paid tool sells

- **Search volume.** Search Console impressions for terms the site already shows up for (a page at position 40 still collects them; they are a floor). Keyword Planner ranges with a Google Ads account. Otherwise rank candidates as strong / some / weak signal: autocomplete in several variants plus competitor pages = strong; autocomplete only = some; neither = weak. Never print an invented volume, and never present `times_seen` as volume.
- **Difficulty.** `scripts/serp_difficulty.py` on the top 10, or the reading by eye: forums, thin pages, old articles and off-type results in the top 10 mean winnable; ten big brands with dedicated pages mean links first.
- **CPC** (the best free proxy for buyer value). Ads above the results mean someone pays for the click; you need a real browser in the market's locale to see them. If neither a tool nor a browser is available, write "CPC unknown" and score with `--conv-rate/--conv-value` or relative signals. Business words (for teams, enterprise, managed, B2B categories like helpdesk, CRM, password manager for companies) carry high prices; hobby and consumer terms low ones.
