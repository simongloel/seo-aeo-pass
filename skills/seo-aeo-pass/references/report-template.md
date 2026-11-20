# Report template

Save as `<out dir>/report.md` (default `~/seo-reports/<YYYY-MM-DD>-<site>/report.md`). Plain sentences, every number with its source and date, no adjectives doing the work of evidence. Keep every section; write "none" where there is nothing.

```markdown
# <site>: SEO and AEO pass, <date>

Mode: <workflow | flat>. Sources: <Search Console range and markets, analytics tool, audit date and page count, keyword tools used, AI visibility source and run count>. Volumes are <measured by X on date | signals, not volumes>.

## Reading

<Three to five sentences: what holds the site back most, and what follows for the next weeks. Example: "Well-titled pages sit at positions 30-90 and the domain has almost no real links, so new pages must target terms a weak domain can win, and links are the main job.">

## Where the site stands

Search: <clicks, impressions, CTR, average position, brand share of clicks, non-brand terms on page one, striking-distance terms, change against the previous period, by market>.
Authority: <the site next to 2-4 competitors, with the source named (a tool's authority score / Tranco / Open PageRank) and what it means>.
AI answers: <mention rate, citation rate, share of voice by engine with run count; top cited domains; AI referral visits from analytics>.
Business: <which entry pages lead to conversions; value of a conversion if known>.

## How keywords were chosen

<The rule as applied: buyer intent and business fit first, then what the site can win, then volume. Kinds of terms dropped on purpose.>

## Keywords

### Build or improve
| Term | Market | Demand (volume + source, impressions, or signal) | CPC (or "unknown") | Difficulty (tool KD, DIY KD, or "not estimated") | Intent | Page |

### Already covered
<term: page that owns it>

### Left out
| Term | Demand | Why not |

### Needs something the product doesn't have
| Feature or offering | Term | Demand | Note |

## Plan

| # | Kind | What | Why (evidence) | Effort | Expected |
<ranked; owner decisions marked>

## Technical findings
<Per issue: count, example URLs, fix / fix when cheap / leave with reason.>

## Claims that are wrong or unprovable
<page, claim, true value, source>

## AI answers: gaps and targets
<prompts where competitors are named and the site isn't; domains to get listed on; pages to build for answers>

## Links
<ranked link and mention targets with why each one; what is prepared for the owner to send>

## Suggestions from other tools
<only when the user pasted some: each item done / doing / not doing, with the reason>

## Not measured
<every data source that was missing or failed, and what it would have added>

## Open checks
<claims left off pages because they could not be verified; visual checks not done>

## Re-read
<two dates (2 and 4 weeks out) and what to compare: positions and clicks for the target URLs, AI mention rate on the same prompts, conversions by entry page>
```

## When volumes are not measured

Use a "Demand" column with one of: a Search Console figure ("22 impressions, position 8"), "strong signal", "some signal", "weak". Say once at the top that these are signals. A reader must never mistake a signal for a measured number.
