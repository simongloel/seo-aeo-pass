#!/usr/bin/env python3
"""Track how often AI assistants mention and cite a brand, the way AI-visibility tools do.

Sends each prompt to each configured assistant (with live web search switched on,
like the consumer apps), several times, and counts per answer:
  - mentioned: the brand or one of its aliases appears in the answer text
  - position: the brand's rank among all tracked brands, by first mention
  - cited: a source URL on the brand's domain is among the answer's citations
  - which competitors are mentioned, which domains are cited

Then reports per assistant and per prompt:
  mention rate     = answers that mention the brand / all answers
  citation rate    = answers that cite the brand's domain / all answers
  share of voice   = brand mentions / mentions of all tracked brands
  average position = mean first-mention rank where mentioned
  top cited domains (where to get mentioned: these are the sources AI reads)

Answers vary between runs, so every prompt runs --samples times (default 5, use 20+ to track a trend: at a 30 % mention rate, 20 runs give about +-10 points) and
the output shows the spread. Treat differences under ~15 points between two
small runs as noise.

Providers and keys (set the ones you have; others are skipped):
  ANTHROPIC_API_KEY  -> Claude with the web search tool
  OPENAI_API_KEY     -> OpenAI Responses API with web_search
  PERPLEXITY_API_KEY -> Perplexity Sonar (search built in)
  GEMINI_API_KEY     -> Gemini with Google Search grounding

  ai_visibility.py --brand "Acme" --alias "Acme CRM" --domain acme.com \
      --competitor "HubSpot=hubspot.com" --competitor "Pipedrive=pipedrive.com" \
      --prompts prompts.txt --samples 3 --json run-2026-11-20.json

Check names and aliases against a few saved answers by hand before trusting the numbers: an
alias that is also a common word, or "formerly <name>", inflates mentions.

prompts.txt: one prompt per line, written the way a buyer would ask
("which CRM is best for a 5-person agency in Germany?"). Lines starting with #
are skipped. Prefix a line with "topic: " to group prompts ("pricing: ...").

Costs money: prompts x samples x providers calls, each with web search.
The script prints the call count and asks before starting unless --yes is set.
"""
import argparse
import collections
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_MODELS = {  # override with --model provider=name; check each provider's current model list
    "anthropic": "claude-opus-5-5",
    "openai": "gpt-5-mini",
    "perplexity": "sonar",
    "gemini": "gemini-2.5-flash",
}
KEYS = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
        "perplexity": "PERPLEXITY_API_KEY", "gemini": "GEMINI_API_KEY"}


def post(url, body, headers, timeout=180):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return json.loads(res.read().decode("utf-8"))


def ask_anthropic(prompt, model, key, country):
    messages = [{"role": "user", "content": prompt}]
    tool = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}
    if country:
        tool["user_location"] = {"type": "approximate", "country": country.upper()}
    text, urls = [], []
    for _ in range(4):  # pause_turn: the server paused a long search turn; send it back to continue
        data = post("https://api.anthropic.com/v1/messages",
                    {"model": model, "max_tokens": 16000, "messages": messages, "tools": [tool],
                     "output_config": {"effort": "low"}, "fallbacks": "default"},
                    {"x-api-key": key, "anthropic-version": "2023-06-01",
                     "anthropic-beta": "server-side-fallback-2026-07-01"})
        if data.get("stop_reason") == "refusal":
            raise RuntimeError(f"refused: {data.get('stop_details')}")
        for block in data.get("content", []):
            if block.get("type") == "text":
                text.append(block.get("text", ""))
                urls += [c.get("url", "") for c in block.get("citations") or [] if c.get("url")]
            elif block.get("type") == "web_search_tool_result" and isinstance(block.get("content"), list):
                urls += [r.get("url", "") for r in block["content"] if r.get("url")]
        if data.get("stop_reason") != "pause_turn":
            break
        messages.append({"role": "assistant", "content": data["content"]})
    return "".join(text), urls


def ask_openai(prompt, model, key, country):
    tool = {"type": "web_search"}
    if country:
        tool["user_location"] = {"type": "approximate", "country": country.upper()}
    data = post("https://api.openai.com/v1/responses", {"model": model, "input": prompt, "tools": [tool]},
                {"Authorization": f"Bearer {key}"})
    text, urls = [], []
    for item in data.get("output", []):
        for part in item.get("content", []) or []:
            if part.get("type") == "output_text":
                text.append(part.get("text", ""))
                urls += [a.get("url", "") for a in part.get("annotations", []) if a.get("url")]
    return "".join(text), urls


def ask_perplexity(prompt, model, key, country):
    data = post("https://api.perplexity.ai/chat/completions",
                {"model": model, "messages": [{"role": "user", "content": prompt}]},
                {"Authorization": f"Bearer {key}"})
    text = data["choices"][0]["message"]["content"]
    urls = list(data.get("citations") or []) + [r.get("url", "") for r in data.get("search_results") or []]
    return text, urls


def ask_gemini(prompt, model, key, country):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={urllib.parse.quote(key)}"
    data = post(url, {"contents": [{"parts": [{"text": prompt}]}], "tools": [{"google_search": {}}]}, {})
    cand = (data.get("candidates") or [{}])[0]
    text = "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", []))
    # Grounding URIs are redirect links; the chunk title carries the source domain.
    chunks = cand.get("groundingMetadata", {}).get("groundingChunks", [])
    urls = [("https://" + c["web"]["title"]) if "." in c.get("web", {}).get("title", "") else c.get("web", {}).get("uri", "")
            for c in chunks if c.get("web")]
    return text, urls


ASK = {"anthropic": ask_anthropic, "openai": ask_openai, "perplexity": ask_perplexity, "gemini": ask_gemini}


def domain_of(url):
    host = urllib.parse.urlsplit(url if "//" in url else "https://" + url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def first_pos(text, names):
    """Earliest whole-word match. Short all-caps names (DO, AWS, OVH) match case-sensitively,
    so "DO" does not match the word "do"; everything else ignores case."""
    hits = []
    for n in names:
        flags = 0 if (n.isupper() and len(n) <= 5) else re.IGNORECASE
        hits += [m.start() for m in re.finditer(r"(?<![\w-])" + re.escape(n) + r"(?![\w-])", text, flags)]
    return min(hits) if hits else None


def analyse(text, urls, brands):
    """brands: [(name, [aliases], domain)], first one is ours."""
    pos = {b[0]: first_pos(text, [b[0]] + b[1]) for b in brands}
    mentioned = sorted((p, n) for n, p in pos.items() if p is not None)
    rank = {n: i + 1 for i, (_, n) in enumerate(mentioned)}
    cited_domains = [domain_of(u) for u in urls if u]
    cited = {b[0]: any(b[2] and (d == b[2] or d.endswith("." + b[2])) for d in cited_domains) for b in brands}
    return {"mentioned": {n: p is not None for n, p in pos.items()}, "rank": rank, "cited": cited,
            "cited_domains": sorted(set(cited_domains))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand", required=True)
    ap.add_argument("--alias", action="append", default=[], help="other names for the brand")
    ap.add_argument("--domain", default="", help="the brand's domain, for citation counting")
    ap.add_argument("--competitor", action="append", default=[], help='"Name=domain.com" or "Name"; repeat')
    ap.add_argument("--prompts", required=True, help="file, one prompt per line")
    ap.add_argument("--samples", type=int, default=5, help="runs per prompt per assistant; 20+ for numbers you will compare over time")
    ap.add_argument("--providers", default="anthropic,openai,perplexity,gemini")
    ap.add_argument("--model", action="append", default=[], help="provider=model, e.g. openai=gpt-5")
    ap.add_argument("--country", default="", help="two-letter country for search location, e.g. de")
    ap.add_argument("--json", help="write every answer and the summary here")
    ap.add_argument("--yes", action="store_true", help="do not ask before spending")
    args = ap.parse_args()

    brands = [(args.brand, args.alias, args.domain.lower())]
    for c in args.competitor:
        name, _, dom = c.partition("=")
        brands.append((name.strip(), [], dom.strip().lower()))
    models = dict(DEFAULT_MODELS, **dict(m.split("=", 1) for m in args.model))
    providers = [p for p in args.providers.split(",") if p in ASK and os.environ.get(KEYS[p])]
    if not providers:
        sys.exit("no provider key set: " + ", ".join(KEYS.values()))
    prompts = []
    with open(args.prompts, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            topic, sep, rest = line.partition(": ")
            prompts.append((topic, rest) if sep and len(topic) < 30 and " " not in topic else ("", line))
    calls = len(prompts) * args.samples * len(providers)
    print(f"{len(prompts)} prompts x {args.samples} samples x {len(providers)} providers ({', '.join(providers)}) = {calls} calls",
          file=sys.stderr)
    if not args.yes and input("start? [y/N] ").strip().lower() != "y":
        return 1

    rows = []
    for topic, prompt in prompts:
        for provider in providers:
            for s in range(args.samples):
                try:
                    text, urls = ASK[provider](prompt, models[provider], os.environ[KEYS[provider]], args.country)
                    rows.append({"topic": topic, "prompt": prompt, "provider": provider, "sample": s,
                                 "answer": text, "urls": urls, **analyse(text, urls, brands)})
                except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError, KeyError, TimeoutError) as err:
                    detail = err.read().decode()[:300] if isinstance(err, urllib.error.HTTPError) else str(err)
                    print(f"# {provider} failed on {prompt[:50]!r}: {detail}", file=sys.stderr)
                time.sleep(0.5)

    me = args.brand
    names = [b[0] for b in brands]

    def summary(sub):
        n = len(sub)
        if not n:
            return None
        mentions = collections.Counter(b for r in sub for b in names if r["mentioned"][b])
        total = sum(mentions.values()) or 1
        ranks = [r["rank"][me] for r in sub if me in r["rank"]]
        return {"answers": n, "mention_rate": round(100 * mentions[me] / n),
                "citation_rate": round(100 * sum(r["cited"][me] for r in sub) / n),
                "share_of_voice": round(100 * mentions[me] / total),
                "avg_position": round(sum(ranks) / len(ranks), 1) if ranks else None,
                "competitor_mention_rate": {b: round(100 * mentions[b] / n) for b in names[1:]}}

    print(f"\n# AI visibility for {me}: {len(rows)} answers\n")
    print("| assistant | answers | mentioned % | cited % | share of voice % | avg position | competitors mentioned % |")
    print("|---|---|---|---|---|---|---|")
    by_provider = {}
    for p in providers + ["all"]:
        s = summary([r for r in rows if p == "all" or r["provider"] == p])
        if s:
            by_provider[p] = s
            comp = ", ".join(f"{b} {v}" for b, v in s["competitor_mention_rate"].items())
            print(f"| {p} | {s['answers']} | {s['mention_rate']} | {s['citation_rate']} | {s['share_of_voice']} | "
                  f"{s['avg_position'] or '-'} | {comp or '-'} |")
    print("\n## per prompt (all assistants)\n\n| prompt | mentioned % | cited % | spread across samples |\n|---|---|---|---|")
    by_prompt = {}
    for _, prompt in prompts:
        sub = [r for r in rows if r["prompt"] == prompt]
        s = summary(sub)
        if not s:
            continue
        by_prompt[prompt] = s
        per_sample = [round(100 * sum(r["mentioned"][me] for r in sub if r["sample"] == i) /
                            max(1, sum(1 for r in sub if r["sample"] == i))) for i in range(args.samples)]
        print(f"| {prompt[:70]} | {s['mention_rate']} | {s['citation_rate']} | {min(per_sample)}-{max(per_sample)} |")
    cited = collections.Counter(d for r in rows for d in r["cited_domains"])
    print("\n## most cited domains (get mentioned on these)\n")
    for d, n in cited.most_common(25):
        print(f"{n}\t{d}")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump({"brand": me, "brands": names, "models": {p: models[p] for p in providers},
                       "summary": by_provider, "by_prompt": by_prompt, "cited_domains": cited.most_common(),
                       "answers": rows}, f, ensure_ascii=False, indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
