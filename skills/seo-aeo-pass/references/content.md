# Pages that rank and get cited

## Match the page to what ranks

| What the top 10 shows | Build |
|---|---|
| Sales and pricing pages | A sales page: what you get, how it works in steps, what it costs, you against the alternatives (including doing it yourself), who it is for, when it is the wrong choice, questions |
| "Best X" lists, comparison sites | An honest ranked list or comparison table with real values, sources and dates. Include competitors; if you won't name them, you can't win this format. Getting approval for naming competitors with prices is usually an owner decision. |
| "<A> vs <B>", "<A> alternatives" | A comparison page: who each fits, a feature and price table with sources and dates, migration steps. These rank fastest against small or new competitors. |
| Guides and how-tos | A guide that answers fully and ends at the product as one honest option, not a pitch in disguise |
| Tools and calculators | A tool, if you can build one. A text page rarely beats a working tool. |
| Forums, Q&A | The result page is unsettled: a thorough page can win |

## What makes the page good, in order

1. **Every claim is true and checkable.** Prices, limits, features, counts, dates, "only/first/best": from the product's own source of truth, never from memory. Wrong prices on live pages cost more trust than any missing tag, and no crawler finds them. Where the site has a build step, render prices and limits from data and add a test that fails on hand-written numbers. If something a buyer relies on cannot be verified, leave the promise out and list it as an open check.
2. **The answer first.** The first two sentences under the H1, and under each question heading, answer the question. AI answers and featured snippets quote these passages; people skim them.
3. **Proof that can be quoted.** Numbers with source and date, short quotes from named people (only real ones), a comparison table with real values. The GEO study (KDD '24) measured +30-40 % visibility in generative answers from statistics, quotations and citations.
4. **"When this is the wrong choice."** A short section that sends the wrong visitors elsewhere. It filters people who would sign up and leave, and it makes the page credible to readers and models.
5. **The exact term up front** in title, H1 and URL slug; title under ~60 characters where the term would otherwise be cut; description within ~155 characters, written to sell the click.
6. **Questions as real headings** with short answers, taken from autocomplete questions, People Also Ask, support. Mark them up as `FAQPage` where it is a real Q&A.
7. **Links in.** Add the page to the site's navigation for its kind (footer column, hub page, related pages), and link it from pages that already rank. A page that only an index links to sits unread. Re-run `site_audit.py` and check no new page has one or zero incoming links.
8. **Who stands behind it.** A real author or team with a short note on why they know, an update date, a way to contact the business. Never invent authors, credentials, reviews or customers.

## Writing it

- Plain sentences, short paragraphs, one idea each. No filler intros ("In today's world..."), no generic conclusions.
- Avoid the words and patterns that mark machine text (see the `human-writing` skill if it is installed): inflated significance, rule-of-three lists, em dashes, "seamless", "robust", "unlock", "delve".
- Write in the language the searcher uses, with the words they type, not the brand's internal terms.
- Partner pages in other languages: translate the facts, re-research the terms. A term that is hard in one market can be easy in another.

## Shipping many pages

Write the first page of each kind yourself; hand batches of 3-5 to helpers with the model page, the fact sources and the rules; ask each to list what it could not verify, and read those lists. They are where wrong claims hide.

Ship in a pace the domain can absorb. On a domain with little authority, 40 pages shipped over five nights were still "unknown to Google" days later, sitemap and IndexNow notwithstanding (IndexNow reaches Bing and Yandex, not Google). Better: fewer pages, each linked from pages Google already crawls, the most important ones sent through "Request indexing" in Search Console, and a re-read in two and four weeks.

## User content on your domain

If users can publish pages on your domain or subdomains (apps, profiles, status pages, docs), keep them on a separate domain or behind `noindex`. Tenant sitemaps and thin user pages pollute the property's coverage, dilute the site's quality signals, and can sink an ad network review.
