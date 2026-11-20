#!/usr/bin/env python3
"""Check whether search engines and AI assistants can reach and read a site.

Standard library only. For a site it checks:
  - robots.txt: which search and AI crawlers are allowed or blocked on / and on
    the sample pages (training bots and answer/search bots are listed apart,
    because blocking one is a policy choice and blocking the other costs citations)
  - Content-Signal lines in robots.txt (Cloudflare's search / ai-input / ai-train)
  - sitemap(s) named in robots.txt and whether they answer
  - llms.txt and llms-full.txt (optional; no major engine is known to rank by it)
  - per sample page: status, noindex, canonical, words in the raw HTML (what a
    crawler that does not run JavaScript sees), structured data types, whether
    the page answers a bot user agent the same as a browser (Cloudflare bot
    blocking shows up here as 403/503 for the bot)

  ai_readiness.py https://example.com
  ai_readiness.py https://example.com --pages /pricing /blog/some-post --json out.json
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BROWSER_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"

# (robots.txt token, owner, role). role: search = classic index, answer = fetched to cite or answer
# a user's question live, train = collected for model training.
BOTS = [
    ("Googlebot", "Google", "search"),
    ("Bingbot", "Microsoft", "search"),
    ("Google-Extended", "Google", "train"),
    ("GPTBot", "OpenAI", "train"),
    ("OAI-SearchBot", "OpenAI", "answer"),
    ("ChatGPT-User", "OpenAI", "answer"),
    ("ClaudeBot", "Anthropic", "train"),
    ("Claude-SearchBot", "Anthropic", "answer"),
    ("Claude-User", "Anthropic", "answer"),
    ("PerplexityBot", "Perplexity", "answer"),
    ("Perplexity-User", "Perplexity", "answer"),
    ("Applebot", "Apple", "search"),
    ("Applebot-Extended", "Apple", "train"),
    ("Meta-ExternalAgent", "Meta", "train"),
    ("Amazonbot", "Amazon", "answer"),
    ("DuckAssistBot", "DuckDuckGo", "answer"),
    ("CCBot", "Common Crawl", "train"),
    ("Bytespider", "ByteDance", "train"),
    ("MistralAI-User", "Mistral", "answer"),
]


def fetch(url, ua=BROWSER_UA, limit=3_000_000):
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "text/html,*/*;q=0.8"})
    try:
        with urllib.request.urlopen(req, timeout=20) as res:
            body = res.read(limit)
            return res.status, dict(res.headers), body.decode(res.headers.get_content_charset() or "utf-8", "replace")
    except urllib.error.HTTPError as err:
        return err.code, dict(err.headers or {}), ""
    except Exception as err:
        return 0, {"error": str(err)}, ""


def parse_robots(text):
    """Returns ({agent_lower: [(allow, path)]}, sitemaps, content_signals)."""
    groups, sitemaps, signals = {}, [], []
    agents, last_was_agent = [], False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        key, value = (x.strip() for x in line.split(":", 1))
        key = key.lower()
        if key == "user-agent":
            if not last_was_agent:
                agents = []
            agents.append(value.lower())
            groups.setdefault(value.lower(), [])
            last_was_agent = True
            continue
        last_was_agent = False
        if key in ("allow", "disallow"):
            for a in agents:
                groups[a].append((key == "allow", value))
        elif key == "sitemap":
            sitemaps.append(value)
        elif key == "content-signal":
            signals.append(value)
    return groups, sitemaps, signals


def allowed(groups, bot, path):
    rules = groups.get(bot.lower())
    if rules is None:
        rules = groups.get("*", [])
    best, verdict = -1, True
    for allow, pattern in rules:
        if pattern == "":
            continue  # "Disallow:" with nothing means allow all
        rx = "^" + re.escape(pattern).replace(r"\*", ".*").replace(r"\$", "$")
        if re.match(rx, path) and len(pattern) > best:
            best, verdict = len(pattern), allow
        elif re.match(rx, path) and len(pattern) == best and allow:
            verdict = True  # Google: the less restrictive rule wins a tie
    return verdict


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def first_hop(url):
    """Status and Location of the first response, without following redirects."""
    opener = urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={"User-Agent": BROWSER_UA}, method="HEAD")
    try:
        with opener.open(req, timeout=20) as res:
            return res.status, ""
    except urllib.error.HTTPError as err:
        return err.code, (err.headers or {}).get("Location", "")
    except Exception:
        return 0, ""


def page_facts(url):
    hop, location = first_hop(url)
    status, headers, text = fetch(url)
    facts = {"url": url, "status": status, "first_hop": hop, "redirects_to": location}
    if status != 200:
        return facts
    head = text[: text.lower().find("</head>")] if "</head>" in text.lower() else text[:20000]
    robots_meta = " ".join(re.findall(r'<meta[^>]+name=["\'](?:robots|googlebot)["\'][^>]*content=["\']([^"\']*)', head, re.I))
    facts["noindex"] = "noindex" in (robots_meta + headers.get("X-Robots-Tag", "")).lower()
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', head, re.I)
    facts["canonical"] = m.group(1) if m else ""
    body = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", text, flags=re.S | re.I)
    facts["raw_html_words"] = len(body.split())
    types = re.findall(r'"@type"\s*:\s*"([^"]+)"', text)
    facts["structured_data"] = sorted(set(types))
    bot_status, _, _ = fetch(url, ua="Mozilla/5.0 (compatible; GPTBot/1.2; +https://openai.com/gptbot)", limit=20000)
    facts["status_for_ai_bot_ua"] = bot_status
    return facts


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("site", help="https://example.com")
    ap.add_argument("--pages", nargs="*", default=[], help="paths to check besides the home page")
    ap.add_argument("--hosts", nargs="*", default=[], help="other hostnames whose robots.txt to check (app., auth., docs. ...)")
    ap.add_argument("--json", help="write the result here")
    args = ap.parse_args()
    base = args.site.rstrip("/")
    out = {"site": base}

    status, _, robots = fetch(base + "/robots.txt")
    out["robots_status"] = status
    groups, sitemaps, signals = parse_robots(robots if status == 200 else "")
    paths = ["/"] + args.pages
    out["bots"] = [{"bot": b, "owner": o, "role": r, "allowed": {p: allowed(groups, b, urllib.parse.urlsplit(p).path or "/") for p in paths},
                    "named_in_robots": b.lower() in groups} for b, o, r in BOTS]
    out["content_signals"] = signals
    out["sitemaps"] = [{"url": s, "status": fetch(s, limit=2000)[0]} for s in sitemaps] or \
                      [{"url": base + "/sitemap.xml", "status": fetch(base + "/sitemap.xml", limit=2000)[0], "note": "not named in robots.txt"}]
    for name in ("llms.txt", "llms-full.txt"):
        out[name] = fetch(f"{base}/{name}", limit=2000)[0]
    out["pages"] = [page_facts(base + (p if p.startswith("/") else "/" + p)) for p in paths]

    print(f"# AI and search readiness: {base}\n")
    print(f"robots.txt: {status}" + (f", Content-Signal: {'; '.join(signals)}" if signals else ", no Content-Signal line"))
    print("\n| bot | owner | role | allowed on / | named in robots.txt |\n|---|---|---|---|---|")
    for b in out["bots"]:
        print(f"| {b['bot']} | {b['owner']} | {b['role']} | {'yes' if b['allowed']['/'] else 'BLOCKED'} | {'yes' if b['named_in_robots'] else 'no (falls back to *)'} |")
    blocked_answer = [b["bot"] for b in out["bots"] if b["role"] in ("answer", "search") and not all(b["allowed"].values())]
    if blocked_answer:
        print(f"\nWARNING: search or answer bots blocked on some paths: {', '.join(blocked_answer)}. These fetch pages to cite them.")
    print("\nsitemaps: " + ", ".join(f"{s['url']} ({s['status']})" for s in out["sitemaps"]))
    print(f"llms.txt: {out['llms.txt']}, llms-full.txt: {out['llms-full.txt']} (optional)")
    for host in args.hosts:
        st, _, txt = fetch(f"https://{host}/robots.txt")
        g, _, _ = parse_robots(txt if st == 200 else "")
        blocked = [b for b, _, r in BOTS if not allowed(g, b, "/")]
        out.setdefault("other_hosts", {})[host] = {"robots_status": st, "rules": sum(len(v) for v in g.values()), "blocked_on_root": blocked}
        print(f"robots.txt on {host}: {st}, {sum(len(v) for v in g.values())} rules, blocked on /: {', '.join(blocked) or 'none'}")
    print("\n| page | status | noindex | raw HTML words | structured data | status for GPTBot UA |\n|---|---|---|---|---|---|")
    for p in out["pages"]:
        st = f"{p['first_hop']} -> {p['redirects_to'] or '?'} -> {p['status']}" if p.get("first_hop") in (301, 302, 303, 307, 308) else p["status"]
        print(f"| {p['url']} | {st} | {p.get('noindex', '')} | {p.get('raw_html_words', '')} | "
              f"{', '.join(p.get('structured_data', [])) or '-'} | {p.get('status_for_ai_bot_ua', '')} |")
    thin = [p["url"] for p in out["pages"] if p.get("status") == 200 and p.get("raw_html_words", 0) < 150]
    if thin:
        print(f"\nWARNING: under 150 words in the raw HTML: {', '.join(thin)}. If the text appears only after JavaScript runs, "
              "most AI crawlers (they do not render) see an empty page. Render on the server or prerender.")
    diff = [p["url"] for p in out["pages"] if p.get("status") == 200 and p.get("status_for_ai_bot_ua") not in (200, None)]
    if diff:
        print(f"\nWARNING: answers a browser but not a bot user agent: {', '.join(diff)}. Check bot protection (WAF, Bot Fight Mode).")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    sys.exit(main())
