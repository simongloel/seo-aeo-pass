# Playbook: reading the measurements, ordering the work, field notes

## Read the site before planning

Say in three to five sentences what holds the site back most. The usual readings, and what follows:

| Signal | Reading | What follows |
|---|---|---|
| Well-titled pages stuck at positions 30-90 for their terms; few real referring domains | Authority problem. Wording won't fix it. | Target low-difficulty and unsettled terms; make links and mentions the main job |
| Pages at 4-15 with impressions, low CTR | Snippet or intent mismatch, or an AI Overview takes the click | Rewrite title and description for the query's intent; check the SERP |
| Many pages "Discovered / Crawled - not indexed" | Google doesn't think the pages are worth it yet, or can't find them through links | Fewer, better pages; internal links from crawled pages; merge thin ones |
| Traffic mostly brand | No non-brand footprint | Pages for buyer terms the site can win, comparison pages against small competitors |
| Non-brand traffic but no conversions from it | Wrong crowd or wrong page type | Re-check intent; add "when this is the wrong choice"; move CTAs; drop free-seeker pages |
| AI answers name competitors, never the site | Not present on the sources AI reads | Get listed on the cited domains; build comparison and list pages |
| Answer bots blocked, or empty raw HTML | Technical | Fix before anything else |

## Order of work

1. Blocking faults: answer bots or Googlebot blocked, pages not answering, JavaScript-only text, canonicals pointing away.
2. Wrong claims on live pages (prices, limits, features).
3. Pages in striking distance (positions 4-20 with impressions): title, intent match, a missing section, internal links. Cheapest gains.
4. New pages for surviving buyer terms, most valuable first, at a pace the domain absorbs.
5. AEO: answer-first sections, comparison tables, consistent facts, `Organization` markup with `sameAs`; then listings on the domains AI cites.
6. Links and mentions: prepared for the owner to send.
7. Measurement gaps: connect Search Console, analytics, Bing Webmaster; set AI referral channels.

Each action in the plan names its evidence and its effort (S/M/L). Mark the decisions that belong to the owner: naming competitors with prices, trademark questions, new products, anything legal, spending money.

## Links and mentions

Content cannot outrun a domain nobody links to. End every pass with a short ranked list of targets:

- list and comparison pages that already rank for the terms you target (search each term, note the lists in the top 10);
- the domains AI answers cite for your prompts (from `ai_visibility.py` or an AI-visibility tool's cited-sources report);
- documentation of products you integrate with or host, when it lists providers;
- where competitors get their links (a backlink tool, Bing Webmaster's free backlink data, or search their name on dev.to, alternativeto, Product Hunt, Reddit);
- cross-posting guides to developer platforms with a canonical link back.

Prepare the entry or the email; sending is the owner's step. Several directories and lists reject submissions written or sent by AI. Don't bulk-submit, don't buy links, and don't disavow spam links without a manual action. Links from your own other sites are not authority; count them separately.

## Measurement traps

- **Quoting notes instead of data.** In one pass an agent claimed a whole language section was not indexed; the API showed two thirds of it had impressions. Re-measure before repeating any old number.
- **Changing the denominator.** Adding prompts to an AI tracker, or including branded prompts, moves the visibility score without anything changing in the world. Compare like-for-like prompt sets, and report unbranded visibility separately.
- **Brand alias collisions.** An alias like "DO" matches the word "do"; "formerly X" counts as a mention of X. Check aliases against a few answers by hand.
- **Silent pipeline failures.** An IndexNow step behind `continue-on-error` failed for weeks unnoticed. Read the real HTTP answer in the log.
- **Lost access.** Search Console access can disappear silently (an unverified owner, a removed service account). Confirm access at the start of every pass.
- **Two tools, two numbers.** One AI visibility tool showed zero AI referrals while the site's own analytics counted hundreds a month. Trust first-party analytics for traffic, the tool for answer content.
- **Own-network links.** Thousands of "external links" in Search Console turned out to come from the owner's own other sites. Real referring domains were close to zero.
- **Readouts too small.** With a handful of conversions a month, the effect of one page on revenue is noise. Use indexing, impressions and positions as the readout for content work.

## Field notes from real passes (2026)

From several passes on a young B2B SaaS domain and a small agency site, measured with Search Console, Matomo, a commercial keyword suite, an AI-visibility tracker and a self-hosted prompt tracker:

- What moved first: comparison pages against small competitors (page one within weeks), "<product> pricing/cost" guides, and long-tail variants of a head term on a dedicated sales page (the head term itself stayed at 30-60).
- What did not move: 40 pages shipped in five nights on a domain with almost no links. Days later, sampled URLs were still "unknown to Google". Shipping speed was not the bottleneck.
- AI assistants cited comparison pages and ranked lists most (together about 60 % of citations), plus third-party list sites. A young brand was confused with similarly named companies until entity markup and consistent facts went out everywhere.
- AI referrals brought sign-ups, and converted to paying customers far less often than search or direct visitors.
- On-site copy changes showed up in what AI assistants told people within days, and changed who arrived.
- A paid ad placement inside an AI assistant brought 11 visits and no sign-ups.
- A self-hosted prompt tracker on paid model APIs with web search used up a 20 USD monthly cap in four days. Budget for runs before promising a trend line.
- Pages for "<Brand> hosting" ran into trademark policies for about a quarter of the products checked.
