#!/usr/bin/env python3
"""Compare domains on free public signals, and give a 0-100 score relative to the set compared.

Sources:
  - Tranco list rank (tranco-list.eu): POPULARITY, i.e. traffic and DNS lookups (CrUX, Cloudflare
    Radar, Umbrella, Majestic, Farsight), not link strength. A platform with API or dashboard
    traffic can out-rank stronger sites. Only the top ~1M domains are listed.
  - Open PageRank 0-10 (openpagerank.com, from Common Crawl's link graph): LINKS. Needs a free
    key in OPR_API_KEY. Without it there is no link signal at all.
  - Common Crawl web graph ranks, if you pass --cc-ranks with a downloaded domain-ranks file
    (harmonic centrality and PageRank; see references/metrics.md 5.2): LINKS.

The "rel_score" column follows references/metrics.md 5.6: percentile ranks within this set,
weighted CC harmonic 0.5, Open PageRank 0.3 (the RD share folded in), Tranco 0.2, renormalised
over the signals present. It is relative to the domains you compare, so always include the site
and the domains that rank above it. Feed it to serp_difficulty.py (auth) and keyword_score.py
(--authority) only together with competitors scored in the same run.

These are not a vendor's authority score (AS, DR, DA) and must not be labelled as such.

  authority.py example.com competitor-a.com competitor-b.com
  OPR_API_KEY=... authority.py --from-file ranking-domains.txt --json out.json
"""
import argparse
import gzip
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def get_json(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "authority-check/1.0", **(headers or {})})
    with urllib.request.urlopen(req, timeout=20) as res:
        return json.loads(res.read().decode("utf-8"))


def tranco(domain):
    """The public API allows about one request per second; back off on 429."""
    for wait in (1.2, 3, 8, 20):
        time.sleep(wait)
        try:
            data = get_json(f"https://tranco-list.eu/api/ranks/domain/{urllib.parse.quote(domain)}")
            ranks = data.get("ranks") or []
            return ranks[0]["rank"] if ranks else None
        except urllib.error.HTTPError as err:
            if err.code != 429:
                print(f"# tranco {domain}: {err}", file=sys.stderr)
                return "error"
        except Exception as err:
            print(f"# tranco {domain}: {err}", file=sys.stderr)
            return "error"
    return "rate limited"


def open_pagerank(domains, key):
    out = {}
    for i in range(0, len(domains), 100):
        q = "&".join("domains%5B%5D=" + urllib.parse.quote(d) for d in domains[i:i + 100])
        try:
            data = get_json(f"https://openpagerank.com/api/v1.0/getPageRank?{q}", {"API-OPR": key})
            for r in data.get("response", []):
                out[r["domain"]] = {"opr": r.get("page_rank_decimal"), "opr_rank": r.get("rank")}
        except Exception as err:
            print(f"# open pagerank: {err}", file=sys.stderr)
    return out


def cc_ranks(path, wanted):
    """Common Crawl domain ranks file: tab-separated #harmonicc_pos, harmonicc_val, #pr_pos, pr_val, host_rev."""
    rev = {".".join(reversed(d.split("."))): d for d in wanted}
    out = {}
    opener = gzip.open if path.endswith(".gz") else open
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 5 and parts[4] in rev:
                out[rev[parts[4]]] = {"cc_harmonic_pos": int(parts[0]), "cc_pagerank_pos": int(parts[2])}
                if len(out) == len(rev):
                    break
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("domains", nargs="*")
    ap.add_argument("--from-file", help="one domain or URL per line")
    ap.add_argument("--cc-ranks", help="Common Crawl domain-ranks.txt(.gz)")
    ap.add_argument("--json")
    args = ap.parse_args()
    items = list(args.domains)
    if args.from_file:
        with open(args.from_file, encoding="utf-8") as f:
            items += [l.strip() for l in f if l.strip() and not l.startswith("#")]
    domains = []
    for d in items:
        host = urllib.parse.urlsplit(d if "//" in d else "https://" + d).netloc.lower()
        host = host[4:] if host.startswith("www.") else host
        if host and host not in domains:
            domains.append(host)
    if not domains:
        ap.error("give at least one domain")

    rows = {d: {"tranco": tranco(d)} for d in domains}
    if os.environ.get("OPR_API_KEY"):
        for d, v in open_pagerank(domains, os.environ["OPR_API_KEY"]).items():
            rows.setdefault(d, {}).update(v)
    if args.cc_ranks:
        for d, v in cc_ranks(args.cc_ranks, domains).items():
            rows[d].update(v)

    def pct(values, higher_better=True):
        """Percentile rank 0..1 within the set; missing values count as weakest."""
        present = [v for v in values.values() if isinstance(v, (int, float))]
        out = {}
        for d, v in values.items():
            if not isinstance(v, (int, float)) or not present:
                out[d] = 0.0
                continue
            better = sum(1 for x in present if (x < v if higher_better else x > v))
            out[d] = better / max(1, len(present) - 1)
        return out

    signals, weights = {}, {}
    tr = {d: (r["tranco"] if isinstance(r.get("tranco"), int) else None) for d, r in rows.items()}
    if any(v is not None for v in tr.values()):
        signals["tranco"], weights["tranco"] = pct(tr, higher_better=False), 0.2
    if os.environ.get("OPR_API_KEY"):
        signals["opr"], weights["opr"] = pct({d: r.get("opr") for d, r in rows.items()}), 0.3
    if args.cc_ranks:
        signals["cc"], weights["cc"] = pct({d: r.get("cc_harmonic_pos") for d, r in rows.items()}, higher_better=False), 0.5
    total = sum(weights.values()) or 1
    link_signals = [k for k in signals if k != "tranco"]
    for d in rows:
        rows[d]["rel_score"] = round(100 * sum(signals[k][d] * w for k, w in weights.items()) / total) if signals else None
        rows[d]["rel_basis"] = "+".join(signals) or "none"

    cols = ["tranco"] + (["opr", "opr_rank"] if os.environ.get("OPR_API_KEY") else []) + \
           (["cc_harmonic_pos", "cc_pagerank_pos"] if args.cc_ranks else []) + ["rel_score"]
    print("| domain | " + " | ".join(cols) + " |\n|---|" + "---|" * len(cols))
    for d in domains:
        print(f"| {d} | " + " | ".join(str(rows[d].get(c)) if rows[d].get(c) is not None else ("not listed" if c == "tranco" else "-")
                                       for c in cols) + " |")
    print(f"\nrel_score: 0-100 within these {len(domains)} domains, from {rows[domains[0]]['rel_basis']}. Tranco: lower rank is more popular.")
    if not link_signals:
        print("WARNING: no link signal. Tranco measures popularity (traffic), not links; do not read this as authority. "
              "Set OPR_API_KEY (free at openpagerank.com) or pass --cc-ranks, or use a backlink tool / Bing Webmaster backlinks.")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=1)


if __name__ == "__main__":
    main()
