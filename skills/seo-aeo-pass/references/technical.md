# Technical audit: what to fix, what to leave

`scripts/site_audit.py` crawls the sitemap and `scripts/ai_readiness.py` checks robots.txt, AI crawlers and raw HTML. Audit tools flag everything with the same alarm. Sort every finding into one of three groups before you report it.

## Fix

- Pages in the sitemap that don't answer 200, or that redirect.
- Broken internal links (the audit lists targets outside the sitemap that fail).
- Missing or duplicate titles and descriptions on pages meant to rank.
- Canonical pointing to another URL on a page that should rank on its own.
- hreflang partners that don't link back, or a set that doesn't name the page itself.
- `noindex` pages listed in the sitemap (either remove from the sitemap or drop the noindex, whichever was meant).
- Pages with zero or one internal link pointing at them. A page only an index links to rarely ranks.
- Thin pages meant to rank (under ~200 words of real text).
- Text that only appears after JavaScript runs. `ai_readiness.py` reports words in the raw HTML; most AI crawlers do not render JavaScript, and Google renders late. Server-render or prerender pages that matter.
- Search or answer bots blocked in robots.txt (OAI-SearchBot, Claude-SearchBot, PerplexityBot, Bingbot, Googlebot) or by a WAF / bot protection (the script compares the status for a bot user agent with a browser's). Blocking training bots (GPTBot, ClaudeBot, Google-Extended, CCBot) is a policy choice; blocking answer bots costs citations.
- Core Web Vitals failing in field data (CrUX p75: LCP > 2.5 s, INP > 200 ms, CLS > 0.1) on the money pages. Lab scores alone are not a finding.

## Fix when cheap

- Titles over ~60-70 characters when the cut removes the search term. A long tail after the term is harmless.
- Descriptions over ~160 characters, or missing on pages with impressions (Google rewrites most snippets anyway; write them for pages where the snippet sells the click).
- Several H1s from a template.
- Images without alt text on content pages.
- Missing `Organization`, `BreadcrumbList`, `Product`/`SoftwareApplication`, `Article` or `FAQPage` markup where the page really is that thing. FAQ rich results are limited to a few site types since 2023; the markup still helps machines read question/answer pairs.

## Leave, and say why in the report

- Title equal to H1.
- Text-to-HTML ratio.
- `nofollow` on outgoing source links, raw URLs in source lists.
- "Invalid structured data" that only means Google's rich result wants a rating, review or author you don't have. Never invent ratings, reviews, authors or customers to satisfy a checker.
- Low word count on pages that are not meant to rank (sign-in, legal, tools).
- llms.txt missing. It is optional; no major engine is known to rank by it. Add it when cheap, never call it a fix for visibility.

## Before changing what a tool flags

- Look for a code comment, a test or a decision record that explains it. Some "problems" are deliberate (noindex on thin app pages, markup without rating in an experiment).
- Don't retitle a page that earns impressions for the words a tool wants to cut. Check Search Console first.
- Don't change URLs that have links or impressions without a 301 from the old one.

## When someone pastes a list from another tool

A site audit tool's issue list, its suggested actions, a consultant's checklist: go through every item and answer done / doing / not doing with the reason. Sort with the groups above. The person should see that nothing was skipped silently.

## Verifying a fix live

- Every changed or new URL answers 200 and is in the sitemap.
- Titles and canonicals on the live HTML (not the template) are the intended ones.
- IndexNow (Bing, Yandex, Seznam, Naver) got the changed URLs and answered 200 or 202: `POST https://api.indexnow.org/indexnow` with `{host, key, keyLocation, urlList}`; the key file must be live at `keyLocation`. Google does not use IndexNow; for two or three pages that matter most, use "Request indexing" in Search Console.
- Look at changed pages at desktop and phone width. If no browser is available, say the visual check is open.
