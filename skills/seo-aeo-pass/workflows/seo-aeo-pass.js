export const meta = {
  name: 'seo-aeo-pass',
  description: 'Full SEO + AEO pass: measure, find buyer keywords, check each against the live results, plan, draft, report',
  whenToUse: 'Run from the seo-aeo skill after the user chose the multi-agent mode and the intake questions are answered.',
  phases: [
    { title: 'Measure', detail: 'search data, technical audit, claims, authority, AI visibility, business value in parallel' },
    { title: 'Diagnose', detail: 'one reading of what holds the site back, and the seed clusters' },
    { title: 'Keywords', detail: 'per cluster: expand, check the live results and score, then try to refute' },
    { title: 'Plan', detail: 'ranked action plan and a completeness critic' },
    { title: 'Draft', detail: 'briefs or full drafts for the top pages' },
    { title: 'Report', detail: 'final report on disk' },
  ],
}

// args (from the skill's intake):
// { site, sitemap, markets: [{country, lang}], business, converts, competitors: [],
//   connectors: {gsc, analytics, keywordTool, aiVisibilityTool, ...}, logs, outDir, skillDir,
//   mode: 'analyze' | 'draft', maxClusters, maxDrafts, date }
const A = args || {}
const OUT = A.outDir
const SK = A.skillDir
const ctx = `Site: ${A.site}. Sitemap: ${A.sitemap || A.site + '/sitemap.xml'}. Markets: ${JSON.stringify(A.markets || [])}.
What the business sells and what a conversion is: ${A.business || 'unknown'}; converts via: ${A.converts || 'unknown'}.
Known competitors: ${(A.competitors || []).join(', ') || 'none given'}. Connected data: ${JSON.stringify(A.connectors || {})}.
Money the pass may spend on paid API calls: ${A.spend || 'none'}. Today: ${A.date}. Skill folder (scripts, references): ${SK}. Write working files under ${OUT}.
Every path below starting with references/ or scripts/ is inside the skill folder.
Rules for every step: never invent a number (search volume, difficulty, traffic). Label every figure with its source and date,
or call it a signal. Read ${SK}/references/metrics.md before quoting or estimating any metric. Read-only on the live site and on
every connected account: no writes, no submissions, no paid reports beyond what the step says.
If writing a file is refused, put its full content into your return value instead.`

const MEASURE_SCHEMA = {
  type: 'object',
  properties: {
    area: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', properties: {
      finding: { type: 'string' }, evidence: { type: 'string' }, impact: { type: 'string', enum: ['high', 'medium', 'low'] },
    }, required: ['finding', 'evidence', 'impact'] } },
    numbers: { type: 'string', description: 'raw baseline numbers worth keeping, with source and date' },
    seeds: { type: 'array', items: { type: 'string' }, description: 'topics or terms this area suggests for keyword research' },
    unavailable: { type: 'array', items: { type: 'string' }, description: 'what could not be measured and why' },
    file: { type: 'string', description: 'path of the detailed notes written under outDir' },
  },
  required: ['area', 'findings', 'numbers', 'seeds', 'unavailable'],
}

const MEASURE = [
  { key: 'search', prompt: `Measure search performance. Read "Reading Search Console correctly" in references/data-sources.md first (alpha-3 country
codes, 2-3 day lag, rows sorted by clicks, subdomains in sc-domain properties, anonymised queries).
Use the Google Search Console MCP if connected (else Bing Webmaster, else say unavailable):
last 28 days and the 28 before, by query, page and country for each market. Report clicks, impressions, CTR, position, brand vs non-brand share,
non-brand queries on page one, striking-distance queries (position 8-30 with impressions), queries with impressions but no page aimed at them,
pages that lost clicks, and CTR far below the expected curve for their position (references/metrics.md has the curve).` },
  { key: 'technical', prompt: `Run the technical audit: python3 ${SK}/scripts/site_audit.py <sitemap> --out ${OUT}/audit.json and
python3 ${SK}/scripts/ai_readiness.py ${A.site} --pages <5 important paths> --json ${OUT}/ai-readiness.json. Add Core Web Vitals field data from the
CrUX API or PageSpeed Insights for the home page and the main money page if reachable. Sort findings with references/technical.md
(fix / fix when cheap / leave and say why). Never call a cosmetic checker warning high impact.` },
  { key: 'claims', prompt: `Read the pages that make product claims (home, pricing, plans, comparison pages, the five most visited articles)
and check each claim a buyer relies on (prices, limits, features, counts, dates, "best"/"only" statements) against the live product or its
own source of truth. List every stale or unprovable claim with the page and the true value. Also judge E-E-A-T signals per references/content.md:
who wrote it, first-hand evidence, sources, update dates. Do not invent authors or reviews as fixes.` },
  { key: 'authority', prompt: `Compare authority and find the real competitors in search. Run python3 ${SK}/scripts/authority.py on the site and
up to 8 competitors (given ones plus the domains that rank for the site's main non-brand terms: search them). Use a connected backlink tool if any
(referring domains and authority for the site and competitors; keep paid usage small and within the spend cap).
Fetch competitors' sitemaps and list which page types and slugs they built (pricing, alternatives, vs, for-industry, integrations, locations).
Say plainly whether the site has an authority problem (well-titled pages stuck at 30-90 = links, not wording).` },
  { key: 'aeo', prompt: `Measure visibility in AI answers. Write 15-25 buyer prompts for the markets (how real buyers ask an assistant, by topic),
save them to ${OUT}/prompts.txt. Then, in this order of preference: an AI-visibility tracking tool if connected (visibility, share of voice,
cited sources); else python3 ${SK}/scripts/ai_visibility.py if any provider key is set and the spend cap allows it (use --yes and keep
prompts x samples x providers within the cap; with no spend allowed, print the command for the user instead of running it); else list the prompts for the user to try in the consumer apps and mark AI visibility as not measured (a web search tool is
not an AI assistant). With a tracking tool, pull overall AND unbranded share of voice and check when its data starts.
If server logs were given (${A.logs || 'none'}), run ${SK}/scripts/ai_crawler_logs.py on them. Report mention rate, share of voice, citation
rate, the domains AI answers cite (these are the outreach targets), and what the cited pages have that ours lack. See references/aeo.md.` },
  { key: 'business', prompt: `Work out who converts and what a visitor is worth. With an analytics connector (GA4 or Matomo MCP): organic entry
pages, AI-assistant referrals, conversions by entry page, country and browser language. Without one, try the Matomo Reporting API or GA4 Data API
if credentials are available, or the product's own database or payment provider read-only; otherwise say it was not measurable.
Then, from the site itself, analytics goals, pricing and anything the intake says:
the offerings that make money, rough value of one conversion, which offerings need no free tier or have a buyer behind them, which pages
convert now. Turn that into seed topics: each offering x the jobs people hire it for x the words buyers use (pricing, alternative, vs, for <role/industry>,
<competitor> alternative, integration names). Mark seeds that bring free-seekers so they can be dropped. See references/keywords.md.` },
]

phase('Measure')
log(`Measuring ${A.site} in ${MEASURE.length} parallel streams`)
const measured = (await parallel(MEASURE.map(m => () =>
  agent(`${ctx}\n\nYour area: ${m.key}.\n${m.prompt}\nWrite detailed notes to ${OUT}/measure-${m.key}.md and return the summary.`,
    { label: `measure:${m.key}`, phase: 'Measure', schema: MEASURE_SCHEMA })))).filter(Boolean)
const gaps = measured.flatMap(m => m.unavailable.map(u => `${m.area}: ${u}`))
if (gaps.length) log(`Not measurable: ${gaps.length} items (listed in the report)`)

phase('Diagnose')
const DIAG_SCHEMA = {
  type: 'object',
  properties: {
    reading: { type: 'string', description: '3-5 sentences: what holds the site back and what follows for this pass' },
    clusters: { type: 'array', items: { type: 'object', properties: {
      name: { type: 'string' }, seeds: { type: 'array', items: { type: 'string' } },
      why: { type: 'string' }, existing_pages: { type: 'array', items: { type: 'string' } },
    }, required: ['name', 'seeds', 'why'] } },
    dropped: { type: 'array', items: { type: 'string' }, description: 'seed themes dropped on purpose, with the reason' },
  },
  required: ['reading', 'clusters', 'dropped'],
}
const diagnosis = await agent(`${ctx}\n\nMeasurements from six parallel streams:\n${JSON.stringify(measured, null, 1)}\n
Write the reading: the one or two things that hold this site back most (authority, intent mismatch, technical, stale claims, no pages for buyer terms,
AI answers citing others). Then group all seeds into at most ${A.maxClusters || 8} clusters worth researching, buyer intent first, each with the
existing pages that already serve it (list titles from the audit at ${OUT}/audit.json to avoid a second page for one term). Drop free-seeker themes.`,
  { label: 'diagnose', phase: 'Diagnose', schema: DIAG_SCHEMA })

phase('Keywords')
const KW_SCHEMA = {
  type: 'object',
  properties: {
    cluster: { type: 'string' },
    keywords: { type: 'array', items: { type: 'object', properties: {
      term: { type: 'string' }, market: { type: 'string' },
      demand: { type: 'string', description: 'measured volume with source and date, or GSC impressions, or strong/some/weak signal' },
      cpc: { type: 'string' }, intent: { type: 'string', enum: ['transactional', 'commercial', 'informational', 'navigational'] },
      serp: { type: 'string', description: 'who ranks in the top 10 and what kind of page; AI Overview present?' },
      difficulty: { type: 'string', description: 'tool KD with source, or DIY estimate with the reasoning from references/metrics.md' },
      value: { type: 'number', description: 'priority score from scripts/keyword_score.py' },
      page_type: { type: 'string' }, target: { type: 'string', description: 'new page slug or existing URL to improve' },
    }, required: ['term', 'demand', 'intent', 'serp', 'difficulty', 'page_type', 'target'] } },
    left_out: { type: 'array', items: { type: 'string' } },
  },
  required: ['cluster', 'keywords', 'left_out'],
}
const VERDICT = {
  type: 'object',
  properties: {
    keep: { type: 'array', items: { type: 'string' }, description: 'terms that survive' },
    killed: { type: 'array', items: { type: 'object', properties: { term: { type: 'string' }, reason: { type: 'string' } }, required: ['term', 'reason'] } },
  },
  required: ['keep', 'killed'],
}
const clusters = (diagnosis && diagnosis.clusters) || []
if (!clusters.length) log('Diagnosis returned no clusters; keyword phase skipped')
const kw = await pipeline(clusters,
  c => agent(`${ctx}\n\nReading: ${diagnosis.reading}\nCluster: ${c.name} (${c.why}). Seeds: ${c.seeds.join('; ')}. Existing pages: ${(c.existing_pages || []).join(', ') || 'none'}.
1. Expand: python3 ${SK}/scripts/keyword_suggest.py --lang <lang> --country <cc> --questions <seeds> for each market (seed bare names and nouns); add GSC queries for this theme
   and competitor slugs from ${OUT}/measure-authority.md.
2. If a keyword tool is connected, batch the 30-50 best candidates through it once in a single report,
   never one call per term. Otherwise use the signal labels.
3. For the 8-15 strongest: look at the live results (WebSearch, or the tool's SERP report). Note page types in the top 10, big brands vs small
   sites vs forums, AI Overview, ads; say which locale you saw and mark features "not seen" when the tool can't show them.
   Estimate difficulty with scripts/serp_difficulty.py (it says "not estimated" without link or authority data; keep that).
4. Score with python3 ${SK}/scripts/keyword_score.py (write a CSV under ${OUT}/kw-<cluster>.csv). Return the scored list.`,
    { label: `kw:${c.name}`, phase: 'Keywords', schema: KW_SCHEMA }),
  (res, c) => !res ? null : agent(`${ctx}\n\nYou are the skeptic. Try to refute each keyword below as a target for this site. Kill a term when:
the searcher does not want what the site sells (free-seeker, student, job seeker, DIY); the top 10 is all big brands and the value is low; the
SERP wants a page type the site cannot offer; an existing page already targets it (cannibalisation); a trademark or licence forbids the page title;
the demand figure is unsupported. Check at least the 5 highest-scored terms against the live results yourself. Default to kill when unsure.\n
Business: ${A.business}. Cluster ${c.name}: ${JSON.stringify(res.keywords)}`,
    { label: `refute:${c.name}`, phase: 'Keywords', schema: VERDICT })
    .then(v => v && ({ ...res, keywords: res.keywords.filter(k => v.keep.includes(k.term)), killed: v.killed })),
)
const kept = kw.filter(Boolean)
log(`${kept.reduce((n, c) => n + c.keywords.length, 0)} keywords survived the skeptic in ${kept.length} clusters`)

phase('Plan')
const PLAN_SCHEMA = {
  type: 'object',
  properties: {
    actions: { type: 'array', items: { type: 'object', properties: {
      rank: { type: 'number' }, kind: { type: 'string', enum: ['fix', 'new-page', 'improve-page', 'aeo', 'links', 'measure', 'owner-decision'] },
      what: { type: 'string' }, why: { type: 'string' }, evidence: { type: 'string' },
      effort: { type: 'string', enum: ['S', 'M', 'L'] }, expected: { type: 'string' }, target: { type: 'string' },
    }, required: ['rank', 'kind', 'what', 'why', 'evidence', 'effort'] } },
    reread: { type: 'string', description: 'what to compare in 2 and 4 weeks' },
  },
  required: ['actions', 'reread'],
}
let plan = await agent(`${ctx}\n\nReading: ${diagnosis && diagnosis.reading}\nMeasurements: ${JSON.stringify(measured)}\nKeywords: ${JSON.stringify(kept)}\n
Build one ranked action plan (max 25). Order by expected business value per effort, using references/playbook.md: stale claims and blocking technical
faults first, then pages for surviving buyer terms, then improving pages in striking distance, then AEO (answer-first sections, comparison tables,
being listed on the domains AI cites), then link targets the owner can act on. Every action names its evidence. Mark owner decisions.`,
  { label: 'plan', phase: 'Plan', schema: PLAN_SCHEMA })
const critic = await agent(`${ctx}\n\nCompleteness critic. Here is the plan: ${JSON.stringify(plan)}. Not measured: ${JSON.stringify(gaps)}.
What is missing or wrong? Check: a market or language not covered, a claim without evidence, a number shown as measured that is a signal, an
action that contradicts a measurement, cannibalisation between two planned pages, nothing for AI answers, nothing for links, re-read dates missing.
Return the corrected plan in the same shape.`, { label: 'critic', phase: 'Plan', schema: PLAN_SCHEMA })
if (critic && critic.actions && critic.actions.length) plan = critic

let drafts = []
if (A.mode === 'draft' && plan) {
  phase('Draft')
  const pages = plan.actions.filter(a => a.kind === 'new-page' || a.kind === 'improve-page').slice(0, A.maxDrafts || 5)
  if (plan.actions.filter(a => a.kind === 'new-page' || a.kind === 'improve-page').length > pages.length)
    log(`Drafting the top ${pages.length} pages only; the rest stay as briefs in the plan`)
  drafts = (await parallel(pages.map((p, i) => () => agent(`${ctx}\n\nDraft this page following references/content.md and the page pattern for its
type: ${JSON.stringify(p)}. Answer first, the exact term in title and H1, a "when this is not the right choice" section, a comparison table where
buyers compare, FAQ with real questions from the keyword research, internal links from and to named existing pages. Only claims you verified on the
site; list unverified ones at the end. Load the human-writing skill if available. Write to ${OUT}/drafts/${i + 1}-<slug>.md and return the path
and the open checks.`, { label: `draft:${i + 1}`, phase: 'Draft' })))).filter(Boolean)
}

phase('Report')
const report = await agent(`${ctx}\n\nWrite the final report to ${OUT}/report.md using ${SK}/references/report-template.md.
If writing the file is refused, return the complete report markdown as your answer instead of a summary.
Reading: ${diagnosis && diagnosis.reading}\nMeasurements: ${JSON.stringify(measured)}\nKeywords kept: ${JSON.stringify(kept)}\nPlan: ${JSON.stringify(plan)}
Not measurable: ${JSON.stringify(gaps)}\nDrafts: ${JSON.stringify(drafts)}\nKeep every figure's source. If the file was written, return its path and a 10-line summary.`,
  { label: 'report', phase: 'Report' })
return { reading: diagnosis && diagnosis.reading, plan, report, gaps }
