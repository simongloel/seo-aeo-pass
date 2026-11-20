# How SEO and AEO tools compute their metrics, and how to approximate them

Researched 2026-11-20 from vendor docs and studies. `[documented]` = the vendor or study states it, source linked. `[inferred]` = our reading, a third-party analysis or a practitioner approximation. Vendor formulas change; re-check a source before quoting a number as current.

**Ground rules.**
- No commercial metric is a measurement. Volume, KD, traffic and authority are all model outputs from panels, crawls and CTR curves. Give ranges, not decimals.
- Scores from different vendors are not interchangeable. One suite's KD 40 is not another's KD 40, and DR 50 is not DA 50.
- First-party data (Search Console, Bing Webmaster Tools, server logs, analytics) beats any third-party estimate for a site you control.

---

## 1. Keyword suites: how the common numbers are modelled

Large all-in-one SEO suites compute the same family of numbers in similar ways. What follows is drawn from their published knowledge-base pages; names and weights differ per vendor, so read it as how such numbers come about, not as one vendor's spec. `[vendor docs]` marks statements taken from vendor documentation.

### 1.1 Search volume
| Aspect | Method | Tag |
|---|---|---|
| Definition | Average monthly Google searches for the keyword in one country database | [vendor docs] |
| Averaging | Total searches over the past 12 months divided by 12. A seasonal keyword's peak month can be far above the number shown | [vendor docs] |
| Inputs | Third-party datasets overlaid with clickstream panels, then extrapolated by machine learning to billions of keywords | [vendor docs] |
| Devices | Mobile and desktop combined | [vendor docs] |
| Global volume | Sum over all country databases | [vendor docs] |

How to approximate it: Google Keyword Planner's `avg_monthly_searches` (also a 12-month average, see §5). For a site you already rank for, Search Console impressions (§5). Keyword Planner merges close variants, so plural and singular can show the same figure. [inferred]

### 1.2 Keyword difficulty (KD, 0-100)
- Estimates how hard it is to reach Google's top 10. Typical bands: 0-14 very easy, 15-29 easy, 30-49 possible, 50-69 difficult, 70-84 hard, 85-100 very hard. [vendor docs]
- Typical inputs: median referring domains of the ranking URLs, median authority of the ranking domains, follow/nofollow ratio of their links, and the SERP layout. [vendor docs]
- One suite published its weights at a 2021 relaunch, still the most detailed public breakdown found [vendor docs]:

| Factor | Weight share |
|---|---|
| Median referring domains of ranking URLs | 41.22 % |
| Median authority score of ranking domains | 16.99 % |
| Search volume | 9.47 % |
| Median follow/nofollow ratio of ranking URLs | 9.17 % |
| Featured snippet present | 4.74 % |
| Instant answer | 4.07 % |
| Branded keyword | 3.50 % |
| Local pack | 3.39 % |
| Knowledge panel | 2.71 % |
| Top stories | 2.03 % |
| People Also Ask | 1.36 % |
| Sitelinks | 1.36 % |
| Word count in keyword | -2.24 % |
| No SERP features | -8.59 % |

- Reading it [inferred]: about 58 % of the weight is links (referring domains plus authority), 9 % the follow ratio and about 19 % SERP layout. KD says almost nothing about content quality or intent match.

### 1.3 Personal difficulty and potential traffic
- **Personal KD**: KD adjusted for one domain, using its topical relevance to the keyword and its metrics against the ranking domains. Proprietary model, same bands. [vendor docs]
- **Potential traffic**: domain-specific traffic estimate from the domain's authority, personal KD, likely position and SERP competition. No formula published. [vendor docs]
- DIY version [inferred]: personal KD ≈ KD adjusted by (your authority − median authority of the top 10) and by how many of your pages already rank for the same cluster (from Search Console). Potential traffic ≈ volume × CTR(expected position), where the expected position comes from where your similar pages rank today.

### 1.4 CPC and competitive density
- **CPC**: the average price advertisers pay Google Ads for a click on this keyword's SERP. Vendors themselves call it unstable and point to Google Ads for live bids. [vendor docs]
- **Competitive density** (0-1): how many advertisers bid on the keyword; nearer 1 = more competition and stronger commercial intent. Paid search only. [vendor docs]
- DIY version [inferred]: Keyword Planner's "Competition" (Low/Medium/High plus a 0-100 index) and the top-of-page bid range are the first-party equivalents (§5). Counting the ads on a live SERP gives a rough density.

### 1.5 Keyword intent
- A machine-learning model over (1) the SERP features shown, (2) intent words in the keyword ("buy", "how", ...) and (3) whether the keyword is branded. Labels: informational, navigational, commercial, transactional. No accuracy figures published. [vendor docs]
- DIY version [inferred]: rules on modifiers (§4.5) plus the SERP layout. Shopping or ad blocks point to transactional, a "best X" listicle top 10 to commercial, People Also Ask plus a featured snippet to informational, one dominant brand result with sitelinks to navigational. A keyword can carry more than one intent.

### 1.6 Organic traffic estimate and traffic cost
- **Formula**: estimated traffic = CTR(position) × keyword volume, summed over a domain's top-100 positions. [vendor docs]
- **Traffic cost / traffic value**: Σ over keywords of (estimated traffic × CPC), i.e. what the same traffic would cost in Google Ads. [vendor docs; formula inferred]
- The CTR curves used are not published and are said to shift with SERP features. [inferred]
- Separate "traffic analytics" products use clickstream panels instead of rankings, filtered and normalised by machine learning. No error rates published. [vendor docs]

### 1.7 Domain authority scores
- 0-100, logarithmic, comparative. A typical modern version combines link power (follow referring domains and their authority), estimated organic traffic, and spam checks: no top-100 rankings, over 90 % dofollow referring domains, links and traffic out of balance, many referring domains on one network, a near-identical backlink profile elsewhere. Weights not published. Recalculated every few weeks. [vendor docs]
- Vendors say these scores are for comparing domains, not for judging one on an absolute scale. None is a Google ranking factor.

### 1.8 Keyword "strategy" or clustering tools
- Input: a few seeds or an uploaded list. Output: topics, then pillar pages, then subpages, prioritised by relevance, volume, KD and SERP features. [vendor docs]
- Clustering groups keywords by intent and SERP similarity (shared top-10 URLs). [vendor docs]
- DIY version [inferred]: two keywords belong on one page when they share at least 3-4 of their top-10 URLs.
- In practice these exports cluster topics; they do not pick buyers (see `keywords.md`).

### 1.9 AI-visibility modules inside keyword suites
- Built from large prompt databases (prompts derived from AI-search clickstream and keyword data), answers captured from the real apps rather than APIs, refreshed daily. [vendor docs]
- **AI visibility score** combines topic coverage (topics where the brand appears) and mention consistency (how often within them). **Mentions** = prompts whose answer names the brand; **citations** = answers that cite the domain. **Prompt volume** is estimated per topic. Vendors call these directional signals. [vendor docs]

---

## 2. AI-visibility trackers: common metric definitions

Dedicated AEO trackers run a set of tracked prompts on several AI platforms (ChatGPT, Google AI Overviews and AI Mode, Gemini, Perplexity, Copilot, Grok, DeepSeek, Claude) per location, and store each answer with its text, brand mentioned yes/no, competitors mentioned, sources consulted and inline citations. Good tools store the exact wording asked, so a reworded prompt does not silently mix series. [vendor docs]

Prompt guidance from vendor docs: start with 10-20 prompts; 50-200 is usually enough. A mix of about 40 % broad / 60 % specific, 30/40/30 awareness/consideration/decision, 20-30 % naming competitors. Reusing SEO keywords as prompts is a poor AEO strategy.

| Metric | Definition | Tag |
|---|---|---|
| Visibility score (0-100) | How prominently the brand appears: mention frequency, position in answers, context, sentiment. Weights not published | [vendor docs] |
| Visibility % / mention rate | Share of answers in the window that name the brand. Rough bands: 80 %+ high, 30-79 % medium, under 30 % low | [vendor docs] |
| Presence rate | Share of tracked prompts that mention the brand at all | [vendor docs] |
| Share of voice | Brand mentions ÷ mentions of all tracked brands, with a rank; change vs the previous equal window | [vendor docs] |
| Average position | Rank of the brand inside the answer when mentioned; null, not 0, when never mentioned | [vendor docs] |
| Sentiment | 0-100 plus a positive/neutral/negative split, per platform | [vendor docs] |
| Citations vs sources | Inline citations = answers that link the page in their text; source uses = answers whose generation consulted it. Kept apart | [vendor docs] |
| Source domains | Per cited domain: citation count, usage share, models, content type (brand, competitor, editorial, social, forum, review, institutional) | [vendor docs] |
| Query fan-out | The sub-queries an AI engine generates while answering a prompt, deduplicated, with frequency | [vendor docs] |
| AEO page score | Share of page-type-specific checks passed: structure, question coverage, sources and proof, fitting schema | [vendor docs] |
| AI traffic | Crawler hits by class (training, search, user-triggered assistant fetch, agent) and human visits referred by AI assistants; joining crawls and visits per path is correlation, not attribution | [vendor docs] |

### 2.1 Reading rules that hold for any tracker
- Visibility is absolute and share of voice is relative; they move independently.

| Pattern | Usual meaning |
|---|---|
| One platform falls, others flat | That engine changed (model or sourcing); your site is probably not the cause |
| All platforms fall together | Your change, or a data-collection gap |
| Visibility flat, share of voice down | A competitor gained; you did not lose |
| Visibility down, share flat | The whole category got quieter |
| Cited sources churned | The answer moved, not your rank |
| Top cited domains don't mention you | Outreach and PR work, not on-site SEO |
| Cited but not recommended | A positioning problem in the answer text |

- A mention gap is a content problem. A citation gap is usually a third-party-source problem: you are missing from the pages the models read.
- Read trends weekly, not daily. A step change is an event: date it and match it against your change log.

---

## 3. Comparable metrics from other vendors

### 3.1 Keyword difficulty
| Vendor | Method | Tag / source |
|---|---|---|
| **Ahrefs KD** (0-100) | Links only. A "weighted average of the number of linking domains to the top-ranking pages" (top 10), outliers removed, plotted on a log scale. On-page factors are ignored. Anchors: KD 0-5 = top pages "barely have any backlinks"; KD ~50 = "a couple of hundred backlinks"; KD 90+ = "thousands". UI example: KD 6 ≈ 7 RDs needed. The weights, outlier rule and log base are not published | [documented] https://help.ahrefs.com/en/articles/72265-what-does-kd-stand-for-in-keywords-explorer , https://ahrefs.com/academy/how-to-use-ahrefs/ahrefs-seo-metrics/keyword-and-search-traffic , https://ahrefs.com/blog/keyword-difficulty/ |
| **Moz KD** (0-100) | Built from the PA/DA of the page-1 results, "modified for projected CTR". Roughly a CTR-weighted average of the top-10 PA | [inferred, Moz help quoted by SEL] https://searchengineland.com/keyword-difficulty-seo-295391 |
| **SE Ranking KD** (0-100) | Proprietary. Uses the quality of the domains in the top 10 and of their backlink profiles | [documented] https://seranking.com/blog/metrics-in-se-ranking/ |
| **DataForSEO Labs KD** (0-100) | The one public formula. Per top-10 result: `x = (domain_rank×0.1 + page_rank×0.9) / 500` (ranks 0-1000). Then `KD = min(1, (max(median(x), mean(x)) − 0.2) / 0.8) × 100`. Per location and language | [documented] https://dataforseo.com/help-center/what-is-keyword-difficulty-and-how-is-it-calculated |

### 3.2 Authority scores
| Metric | Method | Tag / source |
|---|---|---|
| **Ahrefs DR** (0-100, log) | Takes every domain with at least one **followed** link to the target, counting each domain once. Each linking domain's DR is split equally among the unique domains it links to. Ahrefs says the "DR juice" picture is "severely oversimplified". The absolute value is then scaled to 0-100 across the whole Ahrefs database, so DR is relative: if everyone else gains links, your DR can drop. DR 70→71 is a much bigger gap than 20→21 | [documented] https://ahrefs.com/blog/domain-rating/ , https://help.ahrefs.com/ahrefs-terminology/site-explorer/what-is-ahrefs-domain-rating-and-how-is-it-calculated |
| **Ahrefs UR** (0-100, log) | PageRank-like on page-level links, internal and external. Respects nofollow, uses a damping factor, cuts loops and removes some artificial links | [documented] https://help.ahrefs.com/en/articles/72658-what-is-url-rating-ur |
| **Moz DA** (1-100) | DA 2.0 (5 Mar 2019): a machine-learned model (Moz moved from linear to a neural network) that predicts whether a domain ranks in Google. Inputs are linking root domains, link quality patterns and Spam Score. Comparative, not used by Google. A "March 2024 DA update" could not be verified; the sources show 2019 | [documented] https://moz-static.s3.amazonaws.com/products/landing-pages/announcements/Guide_to_Domain_Authority_2.0.pdf ; model detail [inferred] https://searchengineland.com/moz-on-domain-authority-2-0-how-seos-should-and-shouldnt-use-it-313495 |
| **Moz PA** | Page-level version of DA; model updated Sep 2020. No public formula | [inferred] https://www.businesswire.com/news/home/20200901005165/en/Moz-Update-Proprietary-Page-Authority-Metric-Predict |
| **Moz Spam Score** (1-100 %) | Share of sites with similar features that Moz found penalized or banned. 27 features (originally 17 flags). Bands: 1-30 low, 31-60 medium, 61-100 high | [inferred] https://rankmath.com/seo-glossary/spam-score/ |
| **Moz Brand Authority** (2023) | Based on branded search demand; refreshed about every two months. Formula not public | [inferred] https://searchengineland.com/moz-debuts-brand-authority-metric-430325 |
| **Majestic Trust Flow** (0-100, log) | Closeness in the link graph to a manually reviewed set of trusted seed sites | [documented] https://majestic.com/help/glossary |
| **Majestic Citation Flow** (0-100, log) | Link equity from the iterated link network, not raw counts. Replaced ACRank. TF/CF ratio is the common spam check: a low TF with a high CF suggests many weak links [ratio use inferred] | [documented] https://majestic.com/flow-metric-scores |
| **Majestic Topical TF** | More than 800 topic categories. Outbound links pass strength plus a topic label | [documented] https://majestic.com/flow-metric-scores |
| **SE Ranking Domain/Page Trust** (0-100, log) | "Same algorithm that Google's PageRank uses" on SE Ranking's link index | [documented] https://seranking.com/blog/metrics-in-se-ranking/ |
| **DataForSEO Rank** (0-1000) | Original PageRank formula with damping 0.5. Domain rank = log-compressed normalized sum of its pages' PR. `rank_scale=one_hundred` maps it with `sin(rank/636.62)×100` | [documented] https://dataforseo.com/help-center/what_is_rank_in_backlinks_api |

### 3.3 Traffic and visibility
| Metric | Method | Tag / source |
|---|---|---|
| **Ahrefs organic traffic** | Σ over top-100 rankings of volume × CTR(position). CTR comes from "a custom CTR curve for every keyword (based on clickstream data)", but the same article says most keywords use averaged third-party CTRs. Monthly value = average of daily values | [documented] https://help.ahrefs.com/ahrefs-metrics/how-accurate-is-ahrefs-organic-traffic-metric-and-how-do-we-calculate-it , https://help.ahrefs.com/keywords-explorer/faqs-and-troubleshooting/how-does-ahrefs-estimate-the-ctr-in-the-calculation-of-search-traffic |
| **Ahrefs Traffic Potential** | Organic traffic of the current **#1 page** for the keyword, summed over every keyword that page ranks for. Better than single-keyword volume for sizing a page | [documented] https://help.ahrefs.com/en/articles/9046244-what-is-traffic-potential |
| **SE Ranking traffic** | "AI-powered": rankings × volume × CTR, with CTR adjusted for SERP features, branded keywords and intent. Volumes are "ungrouped" from Google's merged close variants. Older forecast formula: T = F×R×I1×I2 | [documented] https://seranking.com/blog/organic-traffic-estimation , https://seranking.com/blog/traffic-forecast/ |
| **Sistrix Visibility Index** | About 1M keywords per country, a representative cross-section by volume, partly rotated. Organic results only, usually 100 per keyword; ads and boxes excluded. Each ranking is weighted by search volume × expected CTR at its position (intent-dependent; no table published). Summed, then normalized to a fixed point total (one page says 100,000 points, others say 1M). 13 countries have daily desktop + mobile data; countries added since 2018 are mobile-only and weekly | [documented] https://www.sistrix.com/visibility-index/calculation |
| **DataForSEO search volume** | Base is Google Ads (rounded, bucketed). Optional clickstream-normalized and Bing-normalized values split Google's merged close variants. Clickstream monthly = clickstream × device/user coefficient; the yearly figure is the 12-month average | [documented] https://dataforseo.com/help-center/sv-cpc-cmp-with-dataforseo-api , https://dataforseo.com/help-center/what-are-clickstream-based-metrics-and-how-do-we-calculate-them |

### 3.4 How accurate are traffic estimates?
| Study | Sample | Result | Tag |
|---|---|---|---|
| Ahrefs (vendor, 2022-05) | 1,635 sites vs GSC, US | Median deviation 49.5 % for the study's own tool, 68.4 % for a competing suite; Pearson 0.76 / 0.74; per-site error from under 5 % to over 1,000 % | [documented, vendor-run] https://ahrefs.com/blog/traffic-estimations-accuracy/ |
| Screaming Frog (2016-06) | 25 UK sites vs GA | Totals between −30 % and +17 % depending on the tool | [inferred] https://www.screamingfrog.co.uk/how-accurate-are-website-traffic-estimators/ |
| OWOX | 787 sites vs GA | Two major estimators 45-61 % off | [inferred, method unchecked] |

Rule [inferred]: a third-party traffic number for one site is accurate to about ±50 % at the median and can be off by 10x. Use these numbers to compare competitors on the same tool, never as a forecast for a client.

---

## 4. Keyword value and CTR

### 4.1 Value formulas
| Metric | Formula | Tag / source |
|---|---|---|
| Ahrefs Traffic Value | Σ per keyword (estimated organic traffic at the current position × CPC). Ahrefs defines it as "the equivalent monthly cost of traffic ... if that traffic was paid via PPC" | [documented] https://help.ahrefs.com/en/articles/1012028 |
| Traffic cost (other suites) | Estimated price of acquiring the same traffic via Google Ads. Same idea as Ahrefs Traffic Value | [vendor docs; formula inferred] |
| Value per visit (ad proxy) | CPC. Expected monthly value of a ranking = volume × CTR(pos) × CPC | [inferred] |
| Conversion-based value | volume × CTR(pos) × conversion rate × value per conversion (AOV or LTV × margin). Google Ads uses value per click = value per conversion × conv. rate (example: $828 × 5 % = $41.40) | [documented] https://support.google.com/google-ads/answer/2796446 ; SEO extension [inferred] |
| Ahrefs Business Potential | 0-3 hand score: 3 = the product is an "irreplaceable solution", 2 = it "helps quite a bit, but it isn't essential", 1 = it "can only be mentioned fleetingly", 0 = "absolutely no way to mention our product". A manual rubric, not computed | [documented] https://ahrefs.com/blog/keyword-research/ |

The keyword score used by `scripts/keyword_score.py` [inferred, our model, not a vendor's]:
```
value  = volume × CTR(target_pos, serp_layout) × intent_weight × business_potential/3 × value_per_visit
effort = f(KD or DIY-KD, gap between your authority and the top-10 median)
priority = value / effort
intent_weight: transactional 1.0, commercial 0.8, informational 0.2-0.4, navigational (other brand) ~0
value_per_visit: own conv. rate × value per conversion if known, else CPC as a ceiling
```

### 4.2 CPC as a commercial signal
- Keyword Planner's "Top of page bid (low range)" ≈ the 20th percentile and "(high range)" ≈ the 80th percentile of what advertisers historically paid for an ad shown at the top of the page, for the chosen locations and network. [documented] https://support.google.com/google-ads/answer/3022575
- No study I found ties CPC to actual conversion value. The nearest is a Disruptive Advertising analysis of about 500k AdWords keywords (Search Engine Land, about 2018): return on ad spend falls as CPC rises, and CTR and CPC predict return only weakly (R² 0.27 / 0.19). https://searchengineland.com/?p=287503 [documented by search summary; page not readable, unverified]
- Reading it [inferred]: CPC is what an average bidder is willing to pay, set by advertisers with ad budgets. It undervalues B2B niches with few advertisers and overvalues keywords dominated by aggregators. Treat it as a ceiling, not as your value.

### 4.3 Organic CTR curves
The studies disagree by a factor of 3-5 at position 1, because they define CTR differently (per query, per impression, branded or not, AIO or not). Pick one curve per model and say which.

| Pos | Sistrix mobile (80M kw, 2020; re-checked 2025) | Backlinko (4M results, 2023; upd. 2025-04) | First Page Sage 2026, no AI answer | First Page Sage 2026, AI answer present | First Page Sage 2026, blended |
|---|---|---|---|---|---|
| 1 | 28.5 % | 27.6 % | 22.6 % | 3.6 % | 7.1 % |
| 2 | 15.7 % | ~15.8 % * | 10.2 % | 1.4 % | 3.0 % |
| 3 | 11.0 % | ~11.0 % * | 5.8 % | 0.8 % | 1.7 % |
| 4 | n/a | ~8.4 % * | 3.7 % | 0.5 % | 1.1 % |
| 5 | n/a | ~6.3 % * | 2.5 % | 0.3 % | 0.7 % |
| 6 | n/a | ~4.9 % * | 1.8 % | 0.3 % | 0.6 % |
| 7 | n/a | ~3.9 % * | 1.3 % | 0.2 % | 0.4 % |
| 8 | n/a | ~3.3 % * | 0.9 % | 0.2 % | 0.3 % |
| 9 | n/a | ~2.7 % * | 0.7 % | 0.1 % | 0.2 % |
| 10 | 2.5 % | ~2.4 % * | 0.5 % | 0.1 % | 0.2 % |

\* Backlinko positions 2-10 are only in charts. These values are commonly cited but not checked against the page.

Sources [documented]:
- Sistrix: https://www.sistrix.com/blog/why-almost-everything-you-knew-about-google-ctr-is-no-longer-valid/. Position 1 CTR depends on the SERP layout: 34.2 % purely organic, 46.9 % with sitelinks, 23.3 % with a featured snippet, 18.8 % with ads, 16.7 % with a knowledge panel, 13.7 % with shopping.
- Backlinko: https://backlinko.com/google-ctr-stats. The top 3 get 54.4 % of clicks, page 2 gets 0.63 %, and moving from #2 to #1 brings +74.5 % clicks.
- First Page Sage: https://firstpagesage.com/reports/google-click-through-rates-ctrs-by-ranking-position/ (Sep 2026; Mar-Aug 2026 data, 3.67B impressions, brand queries excluded). Featured snippet CTR is 11.4 %.
- Advanced Web Ranking: https://www.advancedwebranking.com/seo/organic-ctr (monthly, from GSC data). July 2026, desktop: pos 1 is 20.0 % on all SERPs and 9.7 % with an AIO. All devices: pos 1 is 27.3 % branded vs 19.4 % unbranded. Its monthly values swing a lot (e.g. Apr 2026 AIO pos 1 at 1.96 %), so check the live tool before quoting. [documented, volatile]
- Ahrefs: ~97 % of US desktop clicks go to the top 10. https://ahrefs.com/blog/almost-all-clicks-happen-in-the-top-10-results/

Best practice [inferred]: build your own curve from GSC. Filter to non-brand queries, bucket by rounded average position, and take Σclicks/Σimpressions per bucket. Repeat for queries with and without an AIO (from a SERP API). This beats any published curve for your niche.

### 4.4 AI Overviews, AI Mode and zero-click (2024-2026)
| Source | Date | Finding | Tag |
|---|---|---|---|
| Ahrefs v1 | 2025-04 | 300k keywords. Position 1 CTR on AIO keywords is **−34.5 %** vs forecast (0.026 vs 0.040) | [documented] https://ahrefs.com/blog/ai-overviews-reduce-clicks/ |
| Ahrefs update | 2026-02 | Dec 2023 vs Dec 2025: pos 1 **−58 %** (0.016 vs 0.037 forecast), pos 2 −50.8 %, pos 10 −19.4 % | [documented] https://ahrefs.com/blog/ai-overviews-reduce-clicks-update/ |
| Seer Interactive | 2025-11 | 3,119 informational queries. Q3 2025 organic CTR: 1.45 % with no AIO, 0.52 % with an AIO where the brand is not cited, 0.70 % with an AIO where it is cited. Paid CTR: 13.88 / 4.14 / 7.89 %. Organic CTR with an AIO fell −61 % from Jun 2024 to Sep 2025 | [documented] https://www.seerinteractive.com/insights/aio-impact-on-google-ctr-september-2025-update |
| Pew Research | 2025-07 | 900 US adults, 68,879 searches. Users clicked a result on **8 %** of visits with an AI summary vs **15 %** without. 1 % clicked a link inside the summary | [documented] https://www.pewresearch.org/short-reads/2025/07/22/google-users-are-less-likely-to-click-on-links-when-an-ai-summary-appears-in-the-results/ |
| Amsive | 2025-04 | 700k keywords. AIO: CTR −15.5 % on average, −20 % non-branded, +18.7 % branded, −37 % when an AIO and a featured snippet appear together | [documented by summary] https://www.amsive.com/insights/research/google-ai-overviews-study/ |
| BrightEdge | 2025-05 | First year of AIO: impressions +49 %, click-through about −30 % | [documented, press release] https://brightedge.com/news/press-releases/one-year-google-ai-overviews-brightedge-data-reveals-google-search-usage |
| SparkToro/Datos | 2024-07 | 58.5 % of US and 59.7 % of EU Google searches end without a click. About 374 of 1,000 US searches click to the open web | [documented] https://sparktoro.com/blog/2024-zero-click-search-study-for-every-1000-us-google-searches-only-374-clicks-go-to-the-open-web-in-the-eu-its-360/ |
| SparkToro/Similarweb | 2026-06 | 68 % of US searches zero-click (Jan-Apr 2026); 0.34 % of searches went to AI Mode | [documented] https://sparktoro.com/blog/2025-zero-click-study/ |
| Vendor study, AI Mode | 2025-07 | 92-94 % of AI Mode sessions had no outside click; regular search ~34 % zero-click without an AIO, 43 % with one | [vendor study] |

Model adjustment [inferred]: for keywords whose SERP shows an AIO, multiply the organic CTR of positions 1-3 by about 0.4-0.6, depending on which study you trust (Ahrefs 2026 gives ×0.42 at pos 1). Branded queries lose little or gain. Being cited in the AIO recovers part of the loss (Seer: 0.70 vs 0.52 %).

### 4.5 Intent modifiers
- Vendor examples [vendor docs]: commercial words are "best", "review", "comparison", "X vs Y"; transactional words are "buy", "cheap", "for sale". The four labels are informational, navigational, commercial and transactional.
- Practitioner extension [inferred]: commercial adds "alternative(s) to", "top", "pricing", "price", "cost", "free trial", "software for". Transactional adds "coupon", "discount", "order", "download", "sign up", "near me". Informational: "how", "what", "why", "guide", "tutorial", "examples", "definition". Navigational: brand names, "login", "app".

---

## 5. Free and public data to replicate commercial metrics

All prices and limits were seen 2026-11-20.

### 5.1 Demand (search volume)
| Source | What you get | Limits and gotchas | Tag / source |
|---|---|---|---|
| **Google Keyword Planner / Ads API** | `avg_monthly_searches` (12-month average) plus `monthly_search_volumes[]`, history up to 4 years, competition, top-of-page bid low (≈p20) and high (≈p80). `GenerateKeywordHistoricalMetrics` takes up to 10k keywords per call | Close variants are merged into one canonical idea and volumes are rounded. The API needs a developer token with **Basic** access (15k ops/day; Explorer access blocks planning services) or Standard. Low-spend accounts see ranges (1K-10K…); Google publishes no spend threshold | [documented] https://developers.google.com/google-ads/api/docs/keyword-planning/generate-keyword-ideas , https://developers.google.com/google-ads/api/docs/api-policy/access-levels ; ranges [inferred] https://searchengineland.com/keyword-search-volume-data-disagrees-why-what-to-do-255795 |
| **Google Search Console** | Real impressions, clicks, CTR and average position for queries you already appear for. The truest demand number available for those queries | An impression counts when the link is on the loaded page, even unscrolled. An AI Overview takes **one position** and all its links share it, and AIO/AI Mode traffic is folded into "Web". Rare and personal queries are anonymized and dropped. UI shows 1,000 rows; API returns 25k rows per request, up to ~50k rows/day per search type; 16 months retention; 2-3 day lag | [documented] https://support.google.com/webmasters/answer/7042828 , https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data , https://developers.google.com/search/docs/appearance/ai-features |
| **Google Trends** | 0-100 relative interest: each point is divided by total searches for its place and time, then scaled to the window's max. Sampled | Low-volume terms show 0. Excludes AI Mode/AIO searches. Trends API (alpha, Jul 2025) uses consistent scaling across requests and ~1,800 days, but access is limited | [documented] https://support.google.com/trends/answer/4365533 , https://developers.google.com/search/blog/2025/07/trends-api |
| **Autocomplete** | `https://suggestqueries.google.com/complete/search?client=firefox&hl=<lang>&q=<seed>` returns `[q,[suggestions]]`. Loop over seed + a-z to expand | Undocumented, so it can break or rate-limit. Shows that a query exists, not how big it is | [tested by researcher; undocumented] |
| **People Also Ask** | Question variants for a topic | No official API; scrape the SERP or use a SERP API | [inferred] |
| **Bing Webmaster Tools** | Keyword Research on Bing query data (Bing has called it "raw, not rounded"), free. **AI Performance** (preview since 2026-02-10) shows your URLs cited in Copilot/Bing AI, the grounding queries and citation counts; intent/topic/citation-share views added June 2026. No clicks shown, and ChatGPT is not covered | Bing's share of searches is small, so scale the numbers with a Google/Bing ratio (from your own GSC vs BWT) [inferred] | [documented] https://blogs.bing.com/webmaster/March-2012/4-things-you-may-not-know-about-Bing-Webmaster-too , https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview |
| **Wikipedia pageviews** | `https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/{project}/all-access/user/{Article}/monthly/{YYYYMMDD}/{YYYYMMDD}`. Data since 2015-07 | A topic-interest proxy, not search volume. Useful for comparing entities and spotting trends. Send a descriptive User-Agent | [documented] https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html |
| **Reddit / HN** | Thread counts and upvotes for a topic: proof of real pain, wording for prompts, and the sources AI engines cite (see §6.5) | No volume. Use the Reddit search API or the HN Algolia API (`hn.algolia.com/api/v1/search?query=`) | [inferred] |

How to use them [inferred]:
- For queries you already rank for, impressions over 28 days ÷ 28 × 30 at about position 1-3 ≈ true monthly demand on Google. At lower positions the figure undercounts, because you are not shown for every search.
- Planner volume is an upper-bound bucket for merged variants.
- Use Trends only for seasonality and to compare two terms.

### 5.2 Authority and popularity
| Source | Method | Tag / source |
|---|---|---|
| **Common Crawl web graph** | Host- and domain-level graphs, each from three months of crawls (Jul-Sep 2025: 628.7M hosts, 6.9B edges). Ranked by **harmonic centrality** ("harder to game") and PageRank. Files on `s3://commoncrawl/projects/hyperlinkgraph/<release>/`; newest found Apr-Jun 2026 | [documented] https://commoncrawl.org/blog/host--and-domain-level-web-graphs-july-august-and-september-2025 , https://commoncrawl.github.io/cc-webgraph-statistics |
| **Open PageRank** | Built on Common Crawl, 0-10 with 2 decimals; months without a release are interpolated. Free key: 100 domains per request, ~30k domains/month. Docs now under Keywords Everywhere. Free keys bound to one IPv4 since 2026-11-01 | [documented] https://keywordseverywhere.com/openpagerank/docs |
| **Tranco** | Popularity ranking (traffic, not links), a 30-day average of CrUX, Cloudflare Radar, Farsight, Majestic and Cisco Umbrella, combined by the Dowdall rule | [documented] https://tranco-list.eu/methodology |
| **Cloudflare Radar** | DNS-based ranking from 1.1.1.1: daily top 100, weekly buckets (200 up to 1M). API `/radar/ranking/top` | [documented] https://developers.cloudflare.com/radar/investigate/domain-ranking-datasets/ |
| **CrUX rank** | log10 half-step buckets (top 1k, 5k, 10k, 50k…) of Chrome-visited origins | [documented] https://developer.chrome.com/docs/crux/methodology/metrics |
| **Bing Webmaster Tools backlinks** | Free backlink lists for your site and for any other site you name | [documented] https://blogs.bing.com/webmaster/july-2020/Announcing-the-new-Bing-Webmaster-Tools-(migration-complete) |

### 5.3 Performance
- **CrUX API**: p75 of LCP, INP, CLS, FCP and TTFB over a rolling 28 days, refreshed daily. Query by origin (all pages) or by URL; filter by PHONE, DESKTOP or TABLET. Free, 150 queries/min. **CrUX History API**: weekly series, 25 periods by default, up to 40. [documented] https://developer.chrome.com/docs/crux/api , https://developer.chrome.com/docs/crux/history-api
- PageSpeed Insights API returns lab data (Lighthouse) plus the same CrUX field data. Quota not checked.

### 5.4 Cheap paid APIs (prices seen 2026-11-20)
| Provider | Price | Tag / source |
|---|---|---|
| DataForSEO | $50 minimum top-up, no expiry. Google organic SERP: $0.60 per 1k SERPs (Standard queue), $1.20 Priority, $2.00 Live; each extra 10 results is billed again. Google Ads search volume: $0.06 per task Standard, $0.09 Live, up to 1,000 keywords per task (≈$60 per 1M keywords). Labs: $0.012 per task + $0.00012 per item. Backlinks: from $0.024 per task + $0.000036 per row (old $100/month minimum reported removed) | [documented] https://dataforseo.com/pricing , https://dataforseo.com/pricing/serp/google-organic-serp-api , https://dataforseo.com/pricing/keywords-data/google-ads , https://dataforseo.com/pricing/backlinks |
| SE Ranking API | Included in Core $129/mo and Growth $279/mo; API add-on from $149/mo; pay-as-you-go from €45 per 250k credits | [documented] https://seranking.com/api.html |
| Keywords Everywhere | 1 credit per keyword. $80 for 200k credits, $150 for 500k, $500 for 2M; credits expire after 1 year | [documented] https://keywordseverywhere.com/credits.html |
| Moz API | Reported free tier ~50 rows/month; Starter $20 for 3k rows (moz.com not reachable to verify) | [inferred] https://www.toolsurf.com/moz-api-free-limit-2026/ |

Budget example [inferred]: a 500-keyword DIY KD run costs about $0.30 for SERPs (500 × $0.0006) plus about $5-15 for backlink summaries of 5,000 URLs. Volume for 500 keywords via the Ads endpoint costs $0.06.

### 5.5 DIY keyword difficulty from a live SERP [inferred, our method]
Inputs for each of the top 10 organic URLs (from a SERP API or a manual check):
1. `rd_i` = referring domains to the URL. Free sources: Bing Webmaster Tools backlinks for your own site and competitors, the Ahrefs free backlink checker (top 100 links, per URL), Moz free (a few queries a month), Common Crawl host graph in-degree. Paid: DataForSEO Backlinks `summary`.
2. `auth_i` = domain authority proxy (see DIY authority below).
3. `brand_i` = 1 if the domain is a household brand or a top-1000 Tranco domain.
4. `match_i` = 1 if the page is the same type the query wants (listicle, tool, product, guide).

```
link_term  = clamp( log10(1 + median(rd_i)) / log10(1 + 1000), 0, 1 )      # 1000 RDs ≈ max
auth_term  = median(auth_i) / 100
brand_term = count(brand_i) / 10
serp_term  = 0.10·[AIO] + 0.05·[featured snippet] + 0.05·[≥3 ads] + 0.05·[local pack] + 0.05·[video/shopping] − 0.10·[no features]
gap_term   = share of the top 10 with weak pages (forum threads, thin pages, match_i = 0)

DIY_KD = 100 × clamp( 0.45·link_term + 0.20·auth_term + 0.15·brand_term + 0.20·serp_term − 0.15·gap_term , 0, 1 )
```
The weights copy the published vendor split in §1.2 (about 58 % links, about 19 % SERP layout, the rest volume and brand) and Ahrefs' log scale over RDs. Calibrate the result on 20 keywords where you know a tool's KD. A few UGC results (Reddit, Quora) or outdated pages in the top 10 mean the SERP is beatable even when link_term is high.

### 5.6 DIY authority score [inferred, our method]
```
AUTH = 100 × ( 0.5·pct_rank(CC harmonic centrality of the host)
             + 0.2·pct_rank(Open PageRank 0-10)
             + 0.2·pct_rank(log referring domains from BWT or Common Crawl)
             + 0.1·[domain in Tranco top 1M] · (1 − log10(tranco_rank)/6) )
spam flags (subtract 10-30): RDs ≫ organic visibility, >90 % dofollow, many RDs on one /24, link spikes
```
pct_rank = percentile against the competitor set you are comparing, not the whole web. That matches how vendors say their authority scores should be used: for comparing domains.

---

## 6. Measuring AEO yourself

### 6.1 Prompt tracking you build yourself [inferred unless tagged]
1. **Prompt set.** Write 30-200 prompts the way buyers talk, not your SEO keywords (tracker vendors say the same, §2). Cover several intents, with 3-5 phrasings each:
   - category ("best X for Y")
   - problem ("how do I…")
   - comparison ("A vs B", "alternatives to A")
   - brand ("what is A", "is A good")
   - local/price variants

   SparkToro found that human prompts with the same intent had a semantic similarity of only 0.081, yet still returned similar groups of brands. Sample several phrasings per intent rather than tracking one perfect wording. [documented by study] https://sparktoro.com/blog/new-research-ais-are-highly-inconsistent-when-recommending-brands-or-products-marketers-should-take-care-when-tracking-ai-visibility/
2. **Engines.** Use APIs with web search switched on, because a plain model answers from training data and is a different product:
   - OpenAI Responses API with the web search tool
   - Anthropic Messages API with the web search tool
   - Gemini API with Google Search grounding
   - Perplexity Sonar
   - Google AIO/AI Mode via a SERP API, since there is no official API

   API answers differ from the consumer apps (no personalization or memory, different system prompts). Some commercial trackers capture real app responses rather than API output (§1.9). Label your data "API, search on".
3. **Runs.** Two random answers almost never match: below 1 in 100 for the same brand list, and about 1 in 1,000 for the same order (SparkToro/Gumshoe, 2,961 runs, Jan 2026). Rank is close to meaningless; mention frequency is the metric. Use N ≥ 20 runs per prompt per engine per period; SparkToro used 100 and Conductor 50 (https://www.conductor.com/academy/ai-recommendation-consistency-analysis/). With N runs and mention rate p, the standard error is √(p(1−p)/N). At p = 0.3: N = 20 gives ±10 points, N = 100 gives ±4.6.
4. **Parse each answer.**
   - Brand mention: exact names plus aliases, case-insensitive, word boundaries. Use an LLM pass for misspellings and products.
   - Position of first mention: order among all brands mentioned.
   - Inline citations (URLs in the text or annotations) vs sources consulted, where the API exposes them.
   - Sentiment of the sentences around the brand: an LLM classifier with a fixed rubric, positive/neutral/negative.
   - Store raw answers. Re-parsing later is cheaper than re-running.
5. **Metrics** (the same definitions commercial trackers use, so results stay comparable):
```
mention_rate(brand, prompt, engine) = runs mentioning brand / runs
presence_rate = prompts with mention_rate > 0 / prompts
share_of_voice(brand) = Σ mentions(brand) / Σ mentions(all tracked brands)     # per engine, then averaged or weighted by engine usage
citation_share(domain) = answers citing domain / answers with ≥1 citation
avg_position = mean rank of first mention, only over runs where mentioned (report n)
sentiment = (pos − neg) / (pos + neu + neg), or mapped to 0-100
visibility_index (suite-style) = topic_coverage × mention_consistency
  topic_coverage = topics where brand mention_rate > 0 / topics
  mention_consistency = mean mention_rate over those topics
```
6. **Cadence.** Run weekly and compare 4-week windows; daily numbers are noise (§2.1). Freeze the prompt wording. If you change it, start a new series (good trackers store the exact wording asked for this reason).

### 6.2 AI crawlers in server logs
| Agent | Purpose | robots.txt | IP list | Tag / source |
|---|---|---|---|---|
| GPTBot | OpenAI training | honored | openai.com/gptbot.json | [documented] https://developers.openai.com/api/docs/bots |
| OAI-SearchBot | ChatGPT search index. Blocking it keeps you out of ChatGPT search answers | honored | openai.com/searchbot.json | [documented] same |
| ChatGPT-User | Fetch triggered by a user in ChatGPT | "may not apply" | openai.com/chatgpt-user.json | [documented] same |
| ClaudeBot | Anthropic training | honored | claude.com/crawling/bots.json | [documented] https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler |
| Claude-SearchBot | Claude search index | honored | same | [documented] same |
| Claude-User | Fetch triggered by a user in Claude | honored | same | [documented] same |
| PerplexityBot | Perplexity search index, not training | honored | perplexity.ai/perplexitybot.json | [documented] https://docs.perplexity.ai/guides/bots |
| Perplexity-User | Fetch triggered by a user | "generally ignores" | perplexity.ai/perplexity-user.json | [documented] same |
| Google-Extended | **robots.txt token only, no crawler of its own.** Controls Gemini training and grounding use; "does not affect" Google Search inclusion | n/a | Googlebot ranges | [documented] https://developers.google.com/search/docs/crawling-indexing/google-common-crawlers |
| Googlebot | Also feeds AI Overviews and AI Mode. The only controls there are Googlebot rules, `nosnippet`, `data-nosnippet`, `max-snippet` and `noindex` | honored | googlebot.json | [documented] https://developers.google.com/search/docs/appearance/ai-features |
| Applebot-Extended | Token only ("does not crawl"); training opt-out | n/a | applebot.json | [documented] https://support.apple.com/en-us/119829 |
| Meta-ExternalAgent / -Fetcher | Training and indexing / user fetch (the fetcher "may bypass robots.txt") | partly | - | [documented] https://developers.facebook.com/docs/sharing/webmasters/web-crawlers/ |
| CCBot | Common Crawl (used by many training sets) | honored | index.commoncrawl.org/ccbot.json | [documented] https://commoncrawl.org/ccbot |
| Bingbot | Bing index, which Copilot grounds on | honored | bingbot.json | [inferred] |

Log analysis recipe [inferred]:
1. Match the user agent, then check the IP against the vendor's JSON list. Spoofed UAs are common.
2. Classify each hit as training, search index or user fetch.
3. Count per path per week.
4. User-fetch hits (ChatGPT-User, Claude-User, Perplexity-User) are the closest log signal that a live answer used your page.
5. Search-index hits show eligibility. Training hits say nothing about visibility.
6. Join with sitemap `lastmod` to measure how long a new page waits for its first crawl.

### 6.3 AI referral traffic
- **GA4**: a default **"AI Assistant"** channel since 2026-05-13 (medium `ai-assistant`) [documented] https://support.google.com/analytics/answer/9164320. Reports say it undercounts, so also keep a custom channel group on session source matching:
  `(chatgpt\.com|chat\.openai\.com|perplexity\.ai|gemini\.google\.com|copilot\.microsoft\.com|claude\.ai|chat\.mistral\.ai|meta\.ai|deepseek\.com|grok\.com|you\.com)` [inferred] https://searchenginejournal.com/ga4s-ai-assistant-channel-undercounts-your-ai-traffic-how-to-build-one-that-doesnt/580133
- **Matomo**: since 5.5.0 there is an "AI Assistants" channel type (ChatGPT, Copilot, Gemini, Claude, Le Chat, Meta AI, iAsk, Perplexity; segment `channelType==ai`), applied only to data collected after the upgrade. 5.8.0 added AI chatbot overview reports. [documented] https://matomo.org/changelog/matomo-5-5-0/ , https://matomo.org/faq/reports/what-are-ai-assistants-in-matomo/
- ChatGPT appends `utm_source=chatgpt.com` with no medium, which can land in GA4 "Unassigned". In Oct 2026 the tag briefly disappeared and links opened with `noreferrer`, so visits counted as Direct. Match the UTM tag **and** the referrer. [inferred] https://seroundtable.com/utm-parameters-missing-chatgpt-42299.html
- Google AIO/AI Mode clicks arrive as normal google.com organic traffic and cannot be separated in GSC or analytics. [documented] https://developers.google.com/search/docs/appearance/ai-features

### 6.4 How AI search engines pick sources
- **Google AI Overviews / AI Mode**: "query fan-out" issues many related searches across subtopics and data sources. Deep Search "can issue hundreds of searches". To be a supporting link a page must be indexed and eligible for a snippet; Google states no extra requirements. [documented] https://developers.google.com/search/docs/appearance/ai-features , https://blog.google/products/search/google-search-ai-mode-update/
  - DIY fan-out [inferred]: ask an LLM to break the prompt into 8-15 sub-queries, or read them from tools that log them (an AI-visibility tracker's fan-out report, §2). Check where you rank for each sub-query. A page that ranks for many sub-queries is a likely citation.
- **ChatGPT search**: you must allow OAI-SearchBot to appear [documented, OpenAI bots page]. It is widely reported to use Bing results and partners, but I could not verify this on an OpenAI page [inferred]. Ranking well on Bing is the cheapest lever we can point to [inferred].
- **Perplexity**: its own index, built by PerplexityBot. [documented] https://docs.perplexity.ai/guides/bots
- **Copilot / Bing**: grounded on the Bing index. BWT AI Performance shows the grounding queries (§5.1).

### 6.5 Studies on citation factors (2024-2026)
| Study | Finding | Tag |
|---|---|---|
| GEO paper, Aggarwal et al., KDD '24 | Adding quotations, statistics and source citations raised visibility in generative answers by about 30-40 % (position-adjusted word count). Keyword stuffing did worse than the baseline. On Perplexity: quotations +22 %, statistics up to +37 % | [documented, peer-reviewed] https://arxiv.org/abs/2311.09735 |
| Ahrefs, 75k brands | Brand visibility in AIO correlates most with branded web mentions (Spearman 0.664), then branded anchors 0.527, branded search volume 0.392, backlinks 0.218 | [inferred, vendor study] https://ahrefs.com/blog/ai-overview-brand-correlation/ |
| Ahrefs, AIO citations vs organic rank | Jul 2025: 76 % of cited pages ranked in the top 10. Mar 2026 update (4M URLs, new method): 37-38 % in the top 10, 26 % at positions 11-100, 37 % beyond 100. YouTube is the most cited domain | [inferred; snippet-level, re-check] https://ahrefs.com/blog/ai-overview-citations-top-10/ |
| Profound, ~30M citations (Aug 2024-Jun 2025) | ChatGPT's top source is Wikipedia (47.9 % of its top-10 source share). Perplexity's top source is Reddit (46.7 %). AIO leans on Reddit, YouTube and Quora | [inferred, vendor study] https://www.tryprofound.com/blog/ai-platform-citation-patterns |
| Vendor study | ChatGPT's Reddit citations fell from ~60 % to ~10 % between Aug and Sep 2025; source mixes shift within weeks | [inferred, vendor study] |
| Seer Interactive | Brands cited in an AIO get higher organic CTR (0.70 % vs 0.52 %) than brands not cited | [documented] §4.4 |
| SparkToro/Gumshoe | Brand lists in AI answers are highly inconsistent; track frequency over many runs | [documented by study] §6.1 |

What follows [inferred]:
- Mentions on third-party pages (reviews, listicles, Reddit, Wikipedia, YouTube) predict AI visibility better than backlinks do.
- Organic rank still matters for AIO, but less each year.
- Pages that state numbers, quote people and cite sources are cited more often.
- Source mixes change fast, so check the current cited domains for your prompts (§6.1 parse step) before choosing outreach targets.
