#!/usr/bin/env python3
"""Expand seed terms with Google and Bing autocomplete. No account, no API key.

Autocomplete only lists phrases real people type, so a phrase that shows up is
a demand signal even without a volume number. Each seed is asked plain, with
buyer modifiers before and after it, with question words (for AI answers and
"People also ask"), and with an a-z sweep when --deep is set.

  keyword_suggest.py --lang en --country us "crm for agencies" "invoice software"
  keyword_suggest.py --lang de --country de --seeds-file seeds.txt --deep --json out.json
  keyword_suggest.py --lang en --country gb --questions "password manager"

Output columns: google_seen and bing_seen (how many of the queries returned the
phrase on each engine), intent tag, phrase. These counts are rough strength
signals, never search volumes. Do not print them as one. Seed bare names and
nouns ("<brand>", "invoice software"): a seed that already carries a modifier
("<small brand> alternative") often gets no suggestions at all.
"""
import argparse
import json
import sys
import time
import urllib.parse
import urllib.request

# Words that mark a searcher who wants to buy, rent, compare or replace something.
BUYER = {
    "en": ["pricing", "price", "cost", "best", "vs", "alternative", "alternatives", "for business",
           "for small business", "software", "tool", "service", "provider", "hosting", "managed",
           "agency", "buy", "review", "comparison", "enterprise"],
    "de": ["kosten", "preise", "preis", "beste", "vs", "alternative", "für unternehmen", "software",
           "anbieter", "mieten", "kaufen", "agentur", "vergleich", "test", "erfahrungen", "dsgvo",
           "hosting", "managed"],
    "fr": ["prix", "tarif", "meilleur", "vs", "alternative", "pour entreprise", "logiciel",
           "fournisseur", "agence", "acheter", "avis", "comparatif", "rgpd"],
    "es": ["precio", "precios", "mejor", "vs", "alternativa", "para empresas", "software",
           "proveedor", "agencia", "comprar", "opiniones", "comparativa"],
    "it": ["prezzo", "prezzi", "migliore", "vs", "alternativa", "per aziende", "software",
           "fornitore", "agenzia", "acquistare", "recensioni", "confronto"],
    "nl": ["prijs", "kosten", "beste", "vs", "alternatief", "voor bedrijven", "software",
           "aanbieder", "bureau", "kopen", "ervaringen", "vergelijken"],
}
QUESTIONS = {
    "en": ["how", "what", "which", "why", "who", "can", "is", "best way to", "how much"],
    "de": ["wie", "was", "welche", "warum", "wer", "kann man", "ist", "wie viel", "lohnt sich"],
    "fr": ["comment", "quel", "quelle", "pourquoi", "est-ce que", "combien"],
    "es": ["cómo", "qué", "cuál", "por qué", "cuánto"],
    "it": ["come", "cosa", "quale", "perché", "quanto"],
    "nl": ["hoe", "wat", "welke", "waarom", "hoeveel"],
}
FREE = ["free", "kostenlos", "gratis", "gratuit", "umsonst", "crack", "torrent", "apk", "download",
        "open source", "selfhosted", "self hosted", "raspberry"]
HOWTO = ["how to", "tutorial", "install", "setup", "guide", "anleitung", "installieren", "einrichten",
         "what is", "was ist", "who owns", "meaning", "definition", "example", "beispiel", "reddit", "github"]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (keyword-research script)"})
    with urllib.request.urlopen(req, timeout=10) as res:
        raw = res.read()
    return json.loads(raw.decode(res.headers.get_content_charset() or "utf-8", "replace"))


def ask_google(query, lang, country):
    url = "https://suggestqueries.google.com/complete/search?" + urllib.parse.urlencode(
        {"client": "firefox", "hl": lang, "gl": country, "q": query})
    return get_json(url)[1]


def ask_bing(query, lang, country):
    url = "https://api.bing.com/osjson.aspx?" + urllib.parse.urlencode(
        {"query": query, "mkt": f"{lang}-{country.upper()}"})
    return get_json(url)[1]


def ask(engine, query, lang, country):
    try:
        fn = ask_google if engine == "g" else ask_bing
        return [s for s in fn(query, lang, country) if isinstance(s, str)]
    except Exception as err:  # one blocked request must not end the sweep
        print(f"# {engine}: no answer for {query!r}: {err}", file=sys.stderr)
        return []


def tag(phrase, lang, seeds=()):
    """Intent tag from the words the searcher added to the seed (seed words don't count)."""
    p = f" {phrase.lower()} "
    for seed in seeds:
        for w in seed.lower().split():
            if w not in ("free", "kostenlos", "gratis"):
                p = p.replace(f" {w} ", " ")
    words = p.strip()
    if any(f" {w} " in p for w in FREE):
        return "free"
    if any(f" {w} " in p for w in HOWTO):
        return "howto"
    if any(words.startswith(w + " ") or words == w for w in QUESTIONS.get(lang, QUESTIONS["en"])) or words.endswith("?"):
        return "question"
    if any(f" {w} " in p for w in BUYER.get(lang, BUYER["en"])):
        return "buyer"
    return "-"


def on_topic(phrase, seed, lang="en"):
    """Keep a suggestion only if it shares a topic word (not a modifier) with its seed; engines drift off topic."""
    mods = {w for m in BUYER.get(lang, BUYER["en"]) for w in m.split()}
    tokens = [w for w in seed.lower().split() if len(w) > 2 and w not in mods] or \
             [w for w in seed.lower().split() if len(w) > 2]
    return not tokens or any(w in phrase for w in tokens)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("seeds", nargs="*")
    ap.add_argument("--seeds-file", help="one seed per line, # for comments")
    ap.add_argument("--lang", default="en", help="en, de, fr, es, it, nl (others fall back to English modifiers)")
    ap.add_argument("--country", default="us", help="two-letter country code, e.g. us, gb, de, at, ch, fr")
    ap.add_argument("--engines", default="g", help="g = Google (default), b = Bing, gb = both. Bing adds more, noisier phrases")
    ap.add_argument("--questions", action="store_true", help="also ask question words before the seed")
    ap.add_argument("--no-modifiers", action="store_true", help="only ask the seed itself (fast)")
    ap.add_argument("--deep", action="store_true", help="also ask '<seed> a' .. '<seed> z'")
    ap.add_argument("--json", help="write the full result here")
    ap.add_argument("--pause", type=float, default=0.25, help="seconds between requests")
    args = ap.parse_args()

    seeds = list(args.seeds)
    if args.seeds_file:
        with open(args.seeds_file, encoding="utf-8") as f:
            seeds += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    if not seeds:
        ap.error("give at least one seed")

    seen = {}  # phrase -> {"count": n, "seeds": set, "engines": {engine: count}}
    for i, seed in enumerate(seeds, 1):
        queries = [seed, seed + " "]
        has_modifier = any(f" {m} " in f" {seed.lower()} " for m in BUYER.get(args.lang, BUYER["en"]))
        if not args.no_modifiers and not has_modifier:
            for m in BUYER.get(args.lang, BUYER["en"]):
                queries += [f"{seed} {m}", f"{m} {seed}"]
        if args.questions:
            queries += [f"{q} {seed}" for q in QUESTIONS.get(args.lang, QUESTIONS["en"])]
        if args.deep:
            queries += [f"{seed} {c}" for c in "abcdefghijklmnopqrstuvwxyz"]
        print(f"# seed {i}/{len(seeds)}: {seed!r}, {len(queries) * len(args.engines)} requests", file=sys.stderr)
        for q in queries:
            for engine in args.engines:
                for phrase in dict.fromkeys(p.lower().strip() for p in ask(engine, q, args.lang, args.country)):
                    if not on_topic(phrase, seed, args.lang):
                        continue
                    entry = seen.setdefault(phrase, {"count": 0, "seeds": set(), "engines": {}})
                    entry["count"] += 1
                    entry["seeds"].add(seed)
                    entry["engines"][engine] = entry["engines"].get(engine, 0) + 1
                time.sleep(args.pause)
        if len(seed.split()) > 1 and not any(seed in e["seeds"] for e in seen.values()):
            print(f"# no suggestions for {seed!r}; try the bare name or noun (e.g. {seed.split()[0]!r})", file=sys.stderr)

    order = {"buyer": 0, "question": 1, "-": 2, "howto": 3, "free": 4}
    rows = sorted(seen.items(), key=lambda kv: (order[tag(kv[0], args.lang, kv[1]["seeds"])], -kv[1]["engines"].get("g", 0), -kv[1]["count"], kv[0]))
    print("google_seen\tbing_seen\ttag\tphrase")
    for phrase, e in rows:
        print(f"{e['engines'].get('g', 0)}\t{e['engines'].get('b', 0)}\t{tag(phrase, args.lang, e['seeds'])}\t{phrase}")
    print(f"# {len(rows)} phrases from {len(seeds)} seeds. The counts are signals, not search volumes.", file=sys.stderr)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump([{"phrase": p, "google_seen": e["engines"].get("g", 0), "bing_seen": e["engines"].get("b", 0),
                        "tag": tag(p, args.lang, e["seeds"]), "seeds": sorted(e["seeds"])} for p, e in rows],
                      f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
