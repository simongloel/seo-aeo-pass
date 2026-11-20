# Choosing keywords by what a visitor is worth

Most keyword lists are sorted by volume. Volume says how many people type a phrase, not whether any of them will buy. A site with a few hundred visitors who nearly all fit the offer beats one with thousands who leave. Start from what the business sells and work outward.

## Step 1: know who converts before you pick a single term

If there is any first-party data (analytics goals, CRM, payments, sign-ups by entry page or language), measure first who converts: by country and browser language, by entry page, by referrer, by what they bought. In one 2026 SaaS pass this single measurement showed that visitors in one language converted more than ten times as often as in another, and it set the language and topic order for every page that followed. Without it, the keyword list optimises for the wrong crowd.

Re-measure every pass. Don't quote conversion facts from old notes; they go stale and they were sometimes wrong to begin with.

## Step 2: seeds from the offer

For each thing the business sells: the jobs people hire it for, the words buyers use around it, and the products it replaces.

- `<category> software / service / tool / agency` + qualifiers (for teams, for <industry>, for <role>, <country>, GDPR/HIPAA/...)
- `<category> pricing / cost / price`, `<product> pricing`
- `<competitor> alternative(s)`, `<competitor> vs <competitor>`, `best <category> for <use case>`
- integrations: `<category> for <tool>`, `<tool> <category> integration`
- problem phrases from support tickets, sales calls, Reddit threads

Mark seeds that bring the wrong crowd so they can be dropped: free, crack, download, open source (when you sell the hosted version), jobs, salary, course, definition, tutorial-only.

## Step 3: expand with free sources

1. `scripts/keyword_suggest.py --lang <l> --country <cc> --questions <seeds>`: Google autocomplete (add `--engines gb` for Bing, which adds more and noisier phrases) with buyer modifiers and question words. A phrase that appears is typed by real people; the seen-counts are strength signals, never volumes. Seed bare names and nouns ("<brand>", "invoice software"): for a small brand, a seed that already carries a modifier ("<brand> alternative") often returns nothing, while the bare name returns "<brand> pricing", "<brand> vs ...".
2. Search Console: queries with impressions but no page aimed at them (position over 20), and patterns ("<x> cost", "<x> for <y>"). These come with real impression counts.
3. Competitor sitemaps: which pricing, alternative, vs, for-industry and integration pages they built. A term three competitors built a page for has buyers.
4. Questions from People Also Ask, Reddit, support: these become FAQ sections and AI prompts.

Watch the language people really type. In one pass, German developers typed the English noun plus a German qualifier ("docker hosting deutschland", "... kosten"), while the German verb phrases the site used in its titles ("... hosten") had no autocomplete suggestions at all.

## Step 4: enrich, in one batch, if a tool is connected

Send the 30-50 strongest candidates through the keyword tool once, in a single batch report, for volume, CPC, KD and intent. Use the numbers to rank and to catch surprises, never to generate the list. If several agents share one paid account, give each a unit budget; parallel agents once drained a shared unit pool to zero in an afternoon.

## Step 5: look at the live results for every survivor

Search the term (WebSearch, a SERP API, or a browser for the exact layout) and note what you could see. Many web search tools are fixed to one country and show neither ads nor AI Overviews: say which locale you checked and mark features as "not seen" rather than "absent". A SERP API or a browser in the market's locale gives the real page.

- **page types** in the top 10: sales pages mean buyers; guides mean readers (write a guide that ends at the product); lists mean comparison shoppers (write the honest list).
- **who ranks**: small sites, forums, old or thin pages mean winnable. Ten big brands with dedicated pages mean links first.
- **AI Overview** present: organic CTR drops roughly by half (studies range 0.4-0.6x at position 1). Being cited inside it recovers part.
- **ads**: someone pays for these clicks, so there are buyers.
- **the supplier test**: if your own upstream supplier or a platform you resell ranks #1 for the term, don't compete there.

Estimate difficulty with `scripts/serp_difficulty.py` if no tool KD exists. Score with `scripts/keyword_score.py`.

## The filter

A term earns a page when all three hold:

1. **The searcher wants what is sold**: to buy, rent, replace, compare or hire. Not to learn what something is, not to get it free, not to find the vendor's own login.
2. **The offer fits** (Ahrefs-style business potential 2-3): the product is the answer, or clearly part of it.
3. **The site can win it, or the click pays anyway.** A young domain wins low-difficulty terms and new topics where the results are unsettled. On a contested term, a page is still worth it when CPC is high: position 8 on a valuable term can beat position 1 on a worthless one.

Then sort every candidate into four lists and report all four:

- **Build**: a new page.
- **Already covered**: an existing page targets it. One term, one page. Improve the existing page instead, and when a new page takes a head term, retitle the older one so they stop competing.
- **Needs something the product doesn't have**: report as a product suggestion with the demand next to it.
- **Left out**: with the reason. The reader must see the choice was deliberate.

## Traps seen in real passes

- **Navigational volume.** A product name with thousands of searches is mostly people looking for that product's own site. "<product> hosting" may have 1 % of the volume of "<product>".
- **Ambiguous terms and news spikes.** An acronym can mean a restaurant order or a holiday in another language. A trend line jumping from near zero is news, not a market.
- **CPC outliers.** One extreme CPC on a low-volume term, or the same odd CPC across every country database, is usually model noise. Treat single outliers as suspect, and keep currencies straight.
- **Tool keyword plans.** A "strategy builder" export of 381 terms had 97 with no volume and 115 with difficulty 50+, and suggested legal terms for a withdrawal page. Such exports cluster topics; they don't pick buyers.
- **Impressions without clicks.** Hundreds of impressions at positions 4-8 and zero clicks usually mean the title promises something else than the query wants (a "free" guide ranking for "cheap ... service"), an AI Overview takes the click, or the impressions come from rank trackers. Fix the intent match before chasing more.
- **Trademark and licence rules.** Before a page titled "<Brand> hosting / alternative / for X", read the brand's trademark policy and, for software, its licence. Many forbid exactly that title form (WordPress allows "Hosting for WordPress", not "WordPress Hosting"; Moodle needs written permission; some licences restrict hosting itself). Use a descriptive title and the notice the policy asks for. Unclear cases are the owner's decision.
- **Tests that can't read out.** On a weak domain, one page for a 170-search term gives no measurable revenue signal in a month. Judge new pages by indexing, impressions and position first; revenue per page only when volume allows.
