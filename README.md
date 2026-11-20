# seo-aeo-pass

An agent skill that runs a full SEO and AEO pass on a website: where it ranks, why it doesn't rank higher, which search terms are worth a page, whether ChatGPT, Perplexity, Gemini, Claude and Google's AI Overviews name it, and what to do first. It works from free first-party data (Search Console, your analytics, live search results, autocomplete) and uses paid keyword, backlink or AI-visibility tools only when you have them connected.

It comes out of real passes on a young SaaS domain and a small agency site in 2026, with the lessons from those written in: what moved, what didn't, and which tool numbers misled us.

## What you get

- **A reading** of what holds the site back most (links, intent mismatch, technical faults, wrong claims on live pages, absence from the sources AI answers cite).
- **Keywords chosen by what a visitor is worth**, not by volume. Each term is checked against the live results, scored, and then a skeptic tries to kill it. Left-out terms come with the reason.
- **A ranked plan** of at most 25 actions, each with its evidence and effort, and the decisions that are yours marked as such.
- **Optional page drafts** for the top pages, and a **report** on disk with every number's source.

Nothing is invented: no search volumes from thin air, no fake reviews or authors, no "AI visibility score" without the run count behind it.

## Two modes

At the start the skill asks which one you want:

- **Multi-agent workflow (recommended).** Six measurement streams in parallel, one researcher plus one skeptic per keyword cluster, a critic on the plan. In Claude Code this runs as a [workflow](https://code.claude.com/docs/en/workflows); in other agents it falls back to subagents. Better output, several times the tokens.
- **Flat analysis.** One agent, same steps in sequence, less depth. Cheaper, weaker.

## Install

Any agent that reads `SKILL.md` (Claude Code, Codex, Cursor, Gemini CLI, Copilot and others):

```bash
npx skills add simongloel/seo-aeo-pass
```

In Claude Code use `-a claude-code`, or install it as a plugin, which also registers the workflow as `/seo-aeo-pass:seo-aeo-pass`:

```
/plugin marketplace add simongloel/seo-aeo-pass
/plugin install seo-aeo-pass@simongloel-seo-aeo-pass
```

Manual: copy `skills/seo-aeo-pass/` into `~/.claude/skills/` (or your agent's skills folder).

Then ask something like "run an SEO and AEO pass on example.com" or "why doesn't our pricing page rank".

## Connect your data first

The pass is much better with these two. Both are free.

| Data | MCP server | Setup |
|---|---|---|
| Google Search Console | [AminForou/mcp-gsc](https://github.com/AminForou/mcp-gsc) | `claude mcp add gsc -e GSC_OAUTH_CLIENT_SECRETS_FILE=/abs/path/client_secrets.json -- uvx mcp-search-console` |
| Google Analytics 4 | [googleanalytics/google-analytics-mcp](https://github.com/googleanalytics/google-analytics-mcp) | `claude mcp add analytics-mcp --scope user -e GOOGLE_APPLICATION_CREDENTIALS=<adc.json> -e GOOGLE_CLOUD_PROJECT=<project> -- pipx run analytics-mcp` |
| or Matomo | [Matomo MCP](https://matomo.org/faq/how-to/how-to-configure-the-matomo-mcp-server/) (Cloud built in, self-hosted via the McpServer plugin) | copy the endpoint from Matomo's settings |

Optional: Bing Webmaster Tools (free backlinks, keyword data and Copilot citations), and paid keyword, backlink or AI-visibility tools if you have them. `skills/seo-aeo-pass/references/data-sources.md` has the details.

## Scripts

Standard-library Python 3.9+, no installs. Each prints its usage with `--help`.

| Script | Does |
|---|---|
| `keyword_suggest.py` | Expands seeds through Google autocomplete (Bing optional) with buyer modifiers and question words |
| `keyword_score.py` | Ranks terms by expected value: volume x CTR at the position you can reach x value per visit x intent and fit |
| `serp_difficulty.py` | Estimates keyword difficulty from the top 10 when no tool KD exists |
| `site_audit.py` | Crawls the sitemap: status, titles, descriptions, canonicals, hreflang, structured data, internal links |
| `ai_readiness.py` | robots.txt for search, answer and training bots; raw-HTML word counts; bot vs browser responses; llms.txt |
| `ai_visibility.py` | Asks your buyer prompts to Claude, OpenAI, Perplexity and Gemini with web search on; mention rate, citations, share of voice |
| `ai_crawler_logs.py` | Reads access logs: what AI crawlers fetch, errors they hit, visits referred by AI assistants |
| `authority.py` | Compares domains on popularity (Tranco) and links (Open PageRank, Common Crawl), with a score relative to the set |

`references/metrics.md` explains how commercial SEO and AI-visibility tools compute volume, difficulty, authority, traffic and AI visibility, with sources, and how to approximate each from free data.

## What it contacts

The skill itself sends nothing anywhere. The scripts contact only what you point them at:

- your site (pages, sitemap, robots.txt, llms.txt);
- `suggestqueries.google.com`, and `api.bing.com` if you ask for Bing, for autocomplete (the seed terms are sent);
- `tranco-list.eu`, and `openpagerank.com` if you set `OPR_API_KEY` (domain names are sent);
- the APIs of Anthropic, OpenAI, Perplexity and Google Gemini, only in `ai_visibility.py`, only for providers whose key you set, after showing the call count and asking (your prompts are sent).

MCP servers you connect follow their own terms. The skill asks for a spending cap before any paid call and stays read-only on every account.

## License

MIT
