#!/usr/bin/env python3
"""Read web server access logs and show what AI crawlers fetch and who arrives from AI assistants.

Works with the common and combined log formats (nginx, Apache, Caddy in that
format, most CDNs' raw log exports). Gzipped files are fine. Standard library only.

  ai_crawler_logs.py /var/log/nginx/access.log*
  ai_crawler_logs.py access.log --top 30 --json out.json
  kubectl logs deploy/ingress --since=168h | ai_crawler_logs.py -

Reports:
  - requests per AI crawler, by role (train / answer / search), with status codes
  - the paths each role fetches most (what answer bots fetch is what gets cited)
  - 4xx/5xx served to AI crawlers (blocked or broken pages they tried to read)
  - human visits referred by AI assistants (chatgpt.com, perplexity.ai, ...) by landing page

User agents can be faked. For a real audit, verify IPs against the ranges the
vendors publish (OpenAI, Anthropic, Perplexity, Google and Bing all publish them).
"""
import argparse
import collections
import gzip
import json
import re
import sys

BOTS = [  # (substring in user agent, name, role)
    ("oai-searchbot", "OAI-SearchBot", "answer"), ("chatgpt-user", "ChatGPT-User", "answer"),
    ("gptbot", "GPTBot", "train"), ("claude-searchbot", "Claude-SearchBot", "answer"),
    ("claude-user", "Claude-User", "answer"), ("claudebot", "ClaudeBot", "train"),
    ("perplexity-user", "Perplexity-User", "answer"), ("perplexitybot", "PerplexityBot", "answer"),
    ("google-extended", "Google-Extended", "train"), ("googleother", "GoogleOther", "train"),
    ("googlebot", "Googlebot", "search"), ("bingbot", "Bingbot", "search"),
    ("applebot-extended", "Applebot-Extended", "train"), ("applebot", "Applebot", "search"),
    ("meta-externalagent", "Meta-ExternalAgent", "train"), ("meta-externalfetcher", "Meta-ExternalFetcher", "answer"),
    ("amazonbot", "Amazonbot", "answer"), ("duckassistbot", "DuckAssistBot", "answer"),
    ("mistralai-user", "MistralAI-User", "answer"), ("ccbot", "CCBot", "train"),
    ("bytespider", "Bytespider", "train"), ("youbot", "YouBot", "answer"), ("cohere-ai", "cohere-ai", "train"),
]
AI_REFERRERS = [  # (substring in referrer, assistant)
    ("chatgpt.com", "ChatGPT"), ("chat.openai.com", "ChatGPT"), ("perplexity.ai", "Perplexity"),
    ("claude.ai", "Claude"), ("gemini.google.com", "Gemini"), ("copilot.microsoft.com", "Copilot"),
    ("bing.com/chat", "Copilot"), ("chat.mistral.ai", "Mistral"), ("you.com", "You.com"),
    ("deepseek.com", "DeepSeek"), ("meta.ai", "Meta AI"), ("grok.com", "Grok"), ("phind.com", "Phind"),
]
LINE = re.compile(r'^(\S+) \S+ \S+ \[[^\]]+\] "(?:\S+) (\S+)[^"]*" (\d{3}) \S+(?: "([^"]*)" "([^"]*)")?')
ASSET = re.compile(r"\.(?:css|js|mjs|png|jpe?g|gif|svg|webp|avif|ico|woff2?|ttf|map)(?:\?|$)", re.I)


def lines(paths):
    for p in paths:
        if p == "-":
            yield from sys.stdin
        elif p.endswith(".gz"):
            with gzip.open(p, "rt", encoding="utf-8", errors="replace") as f:
                yield from f
        else:
            with open(p, encoding="utf-8", errors="replace") as f:
                yield from f


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", nargs="+", help="log files, or - for stdin")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--host", help="only count lines whose path or referrer mention this host (multi-site logs)")
    ap.add_argument("--json", help="write the full counts here")
    args = ap.parse_args()

    per_bot = collections.Counter()
    status_by_bot = collections.defaultdict(collections.Counter)
    paths_by_role = collections.defaultdict(collections.Counter)
    errors = collections.Counter()
    referred = collections.defaultdict(collections.Counter)
    total = parsed = 0
    for line in lines(args.logs):
        total += 1
        m = LINE.search(line)
        if not m:
            continue
        parsed += 1
        _ip, path, status, referrer, ua = m.groups()
        referrer, ua = (referrer or "").lower(), (ua or "").lower()
        if args.host and args.host not in line:
            continue
        bot = next(((n, r) for s, n, r in BOTS if s in ua), None)
        if bot:
            name, role = bot
            per_bot[(name, role)] += 1
            status_by_bot[name][status] += 1
            if not ASSET.search(path):
                paths_by_role[role][path.split("?")[0]] += 1
            if status[0] in "45":
                errors[(name, status, path.split("?")[0])] += 1
            continue
        if ASSET.search(path):
            continue
        assistant = next((a for s, a in AI_REFERRERS if s in referrer), None)
        if not assistant and re.search(r"[?&]utm_source=(chatgpt\.com|perplexity|copilot|claude)", path, re.I):
            assistant = re.search(r"utm_source=([^&]+)", path, re.I).group(1)
        if assistant:
            referred[assistant][path.split("?")[0]] += 1

    print(f"# AI crawlers and AI referrals: {parsed} of {total} lines parsed\n")
    if parsed == 0:
        print("No line matched the common/combined log format. Convert the log first.")
        return 1
    print("| crawler | role | requests | status codes |\n|---|---|---|---|")
    for (name, role), n in per_bot.most_common():
        codes = ", ".join(f"{c} {k}" for c, k in status_by_bot[name].most_common(4))
        print(f"| {name} | {role} | {n} | {codes} |")
    for role in ("answer", "train", "search"):
        if paths_by_role[role]:
            print(f"\n## most fetched by {role} bots")
            for p, n in paths_by_role[role].most_common(args.top):
                print(f"{n}\t{p}")
    if errors:
        print("\n## errors served to AI crawlers")
        for (name, status, p), n in errors.most_common(args.top):
            print(f"{n}\t{status}\t{name}\t{p}")
    print("\n## human visits referred by AI assistants")
    if not referred:
        print("none found (many assistants send no referrer; ChatGPT adds utm_source=chatgpt.com)")
    for assistant, pages in sorted(referred.items(), key=lambda kv: -sum(kv[1].values())):
        print(f"{assistant}: {sum(pages.values())} visits; top pages: " +
              ", ".join(f"{p} ({n})" for p, n in pages.most_common(5)))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"bots": {f"{n}|{r}": c for (n, r), c in per_bot.items()},
                       "paths_by_role": {r: dict(c.most_common(200)) for r, c in paths_by_role.items()},
                       "errors": [[n, s, p, c] for (n, s, p), c in errors.most_common(200)],
                       "referred": {a: dict(c) for a, c in referred.items()}}, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
