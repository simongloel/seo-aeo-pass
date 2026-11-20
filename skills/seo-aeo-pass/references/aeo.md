# AEO: being named and cited in AI answers

AEO (answer engine optimisation, also called GEO) is about ChatGPT, Claude, Gemini, Perplexity, Copilot, Google AI Overviews and AI Mode naming your brand and linking your pages. Measurement details and study numbers are in `metrics.md` section 6. This file is the part you act on.

## What decides whether you show up

In rough order of what the 2024-2026 studies support:

1. **Being mentioned on the pages the models read.** Ahrefs (75k brands): branded web mentions correlate with AI Overview visibility at 0.66, backlinks at 0.22. ChatGPT leans on Wikipedia, Perplexity on Reddit, AI Overviews on Reddit, YouTube and Quora (Profound, 30M citations). Comparison and "best X" list pages that already rank are the other big source. A citation gap is usually a third-party problem, not an on-site one.
2. **Ranking in classic search.** AI Overviews and AI Mode fan a question out into many sub-searches and cite pages that rank for them. ChatGPT search, Copilot and Perplexity use their own or Bing's index. Being indexed and snippet-eligible on Google and Bing is the entry ticket; Bing is the cheapest lever many sites ignore.
3. **Being reachable.** Answer bots allowed in robots.txt and not blocked by a WAF (OAI-SearchBot, ChatGPT-User, Claude-SearchBot, Claude-User, PerplexityBot, Perplexity-User, Bingbot, Googlebot). Text in the raw HTML, because most AI fetchers don't run JavaScript. `scripts/ai_readiness.py` checks both.
4. **Pages that are easy to quote.** The GEO paper (KDD '24) measured +30-40 % visibility from adding statistics, quotations and cited sources; keyword stuffing made it worse. In practice: answer the question in the first two sentences under a heading that is the question; state numbers with their source and date; use comparison tables with real values; keep one idea per paragraph so a passage stands alone.
5. **Consistent facts about you.** Name, what you sell, prices, where you operate, who it is for: the same on your site, Wikipedia/Wikidata if you qualify, directories, review sites and social profiles. Models repeat what most sources agree on. `Organization` markup with `sameAs` links helps machines join them.

llms.txt is optional. No major engine has said it ranks by it. Cheap to add, never a fix.

## Measuring

Pick the best available, in this order:

1. **An AI-visibility tracking tool** if one is connected: visibility, share of voice, cited sources, query fan-out; its drop-investigation report if it has one. Read-only.
2. **`scripts/ai_visibility.py`** with any provider key: runs your prompts through the APIs with web search on, counts mention rate, citation rate, share of voice, position, and the domains cited. Label results "API, search on"; consumer apps answer differently.
3. **By hand**: ask 8-10 prompts in the consumer apps (the user, or a browser tool), note who is named and cited. Enough to find the gap, not to track a trend. A web search tool is not an AI assistant; its results say nothing about AI answers.

Caveats for tracking tools (seen in practice; likely similar across vendors):

- Pull **overall and unbranded** share of voice. Prompts that name the brand inflate the headline: in one project overall share was 7.1 % and unbranded 1.4 %.
- Check when the project's data starts before reading any "change" figure. A three-day-old project can still show a "30-day change".
- Adding or rewording prompts changes the denominator. Compare like-for-like prompt sets.
- Crawler and traffic reports may count every subdomain; filter by host.
- Referral counts depend on the tool's tracking setup; when first-party analytics disagrees, trust analytics for traffic.
- Some calls return very large payloads; ask for summaries or narrow by topic or date.

Rules for numbers you will compare over time:

- Answers almost never repeat (SparkToro/Gumshoe: under 1 in 100 runs give the same brand list). Track **mention rate over many runs**, not rank. 20 runs per prompt per engine at a 30 % mention rate give about ±10 points; 100 runs about ±5.
- Freeze the prompt wording; a reworded prompt is a new series.
- Compare 4-week windows weekly. A single low day is noise.
- Write prompts the way buyers ask an assistant ("which CRM works for a 5-person agency that needs GDPR?"), not your SEO keywords. 15-50 prompts across awareness, comparison and decision; 20-30 % should name a competitor.

How to read changes (these hold for any tracking tool):

| Pattern | Usual meaning |
|---|---|
| One engine falls, others flat | That engine changed its model or sources; probably not you |
| All engines fall together | Your change, or a data gap |
| Visibility flat, share of voice down | A competitor gained |
| Visibility down, share flat | The category got quieter |
| Top cited domains don't mention you | Outreach, not on-site work |
| Cited but not recommended | A positioning problem in how sources describe you |

First-party signals:

- **AI referrals**: GA4 has an "AI Assistant" default channel since May 2026 (it undercounts; also match session source against `chatgpt.com|chat.openai.com|perplexity.ai|gemini.google.com|copilot.microsoft.com|claude.ai|chat.mistral.ai|meta.ai|deepseek.com|grok.com`). Matomo 5.5+ has an "AI Assistants" channel type. ChatGPT adds `utm_source=chatgpt.com`; match the tag and the referrer. Google AI Overview clicks look like normal Google organic and cannot be separated.
- **Server logs**: `scripts/ai_crawler_logs.py`. User-fetch bots (ChatGPT-User, Claude-User, Perplexity-User) hitting a page is the closest log signal that a live answer used it. Training bots say nothing about visibility.
- **Bing Webmaster Tools > AI Performance** shows the queries for which Copilot cited your URLs.

## What to do, by gap

| Gap found | Action |
|---|---|
| Answer bots blocked or pages empty without JavaScript | Fix first; nothing else matters until then |
| Not mentioned, competitors are | Get onto the pages AI cites for those prompts: list articles, comparison sites, directories, Reddit threads (as a real participant, disclosed), YouTube. The `cited_domains` output is the target list. |
| Mentioned, not cited | Build the page the answer needs: a comparison table, a pricing explainer, a "best X for Y" page that is honest about when you are not the answer |
| Cited, described wrong | Fix the facts at the source: your pricing page, your docs, the directory listing, Wikipedia talk page |
| Strong on one engine only | Check that engine's index: Bing for ChatGPT/Copilot, Perplexity's own crawler, Google for AIO |
| Good on brand prompts, absent on category prompts | You lack category authority: category pages, original data others quote, being listed by third parties |

## What not to do

- No fake reviews, sock-puppet Reddit posts, invented statistics or hidden text aimed at bots. Models and platforms detect and punish it, and it is the kind of thing a person would be embarrassed to see in the report.
- Don't serve bots different content from people.
- Don't promise AI visibility numbers. Report what was measured, with the run count.
