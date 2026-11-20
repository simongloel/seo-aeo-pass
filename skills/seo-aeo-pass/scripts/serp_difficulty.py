#!/usr/bin/env python3
"""Estimate keyword difficulty from what actually ranks, without a paid tool.

Implements the DIY difficulty in references/metrics.md (section 5.5). You look
at the top 10 for a term (WebSearch, a SERP API, or by hand) and fill one row
per ranking URL. Columns:

  term       the keyword
  pos        1-10
  url        the ranking URL
  rd         referring domains to that URL, if you have it (Bing Webmaster Tools,
             a free backlink checker, Common Crawl in-degree); empty = unknown
  auth       domain authority proxy 0-100 (scripts/authority.py, or a tool's score)
  brand      1 if a household brand or Tranco top-1000 domain, else 0
  weak       1 if the result is a forum thread, a thin or outdated page, or the
             wrong page type for the query; else 0
  features   space-separated SERP features seen for the term (same on every row
             or only on the first): aio snippet ads3 local video shopping none.
             Leave empty if you could not see the real result page (most web-search
             tools show neither ads nor AI Overviews); the output then says "unknown".

Output per term: DIY_KD 0-100, the parts it is made of, and a plain reading
("winnable for a young domain", ...). Calibrate once on 10-20 terms where you
know a tool's KD; the weights follow published vendor splits (mostly links, some SERP layout) on a log scale.

  serp_difficulty.py serps.csv
  serp_difficulty.py serps.csv --site-auth 12 --json kd.json
"""
import argparse
import collections
import csv
import json
import math
import statistics


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def score(rows):
    rds = [r for r in (num(x.get("rd")) for x in rows) if r is not None]
    auths = [a for a in (num(x.get("auth")) for x in rows) if a is not None]
    brands = sum(1 for x in rows if (x.get("brand") or "").strip() == "1")
    weak = sum(1 for x in rows if (x.get("weak") or "").strip() == "1")
    feats = set()
    for x in rows:
        feats |= set((x.get("features") or "").lower().split())
    n = max(len(rows), 1)
    link = clamp(math.log10(1 + statistics.median(rds)) / math.log10(1001)) if rds else None
    auth = statistics.median(auths) / 100 if auths else None
    serp = (0.10 * ("aio" in feats) + 0.05 * ("snippet" in feats) + 0.05 * ("ads3" in feats) +
            0.05 * ("local" in feats) + 0.05 * bool({"video", "shopping"} & feats) - 0.10 * ("none" in feats))
    if link is None and auth is not None:
        link, basis = auth, "no RD data: authority used for the link part"
    elif link is None:
        return {"diy_kd": None, "median_rd": None, "median_auth": None, "brands": brands, "weak_results": weak,
                "features": sorted(feats), "results": len(rows), "basis": "insufficient data: no RD or authority column"}
    else:
        basis = "RD + authority"
    if len(rows) < 10:
        basis += f"; only {len(rows)} results seen"
    if not feats:
        basis += "; SERP features unknown"
    auth = auth if auth is not None else link
    kd = 100 * clamp(0.45 * link + 0.20 * auth + 0.15 * brands / n + 0.20 * serp - 0.15 * weak / n)
    return {"diy_kd": round(kd), "median_rd": statistics.median(rds) if rds else None,
            "median_auth": round(statistics.median(auths)) if auths else None, "brands": brands,
            "weak_results": weak, "features": sorted(feats), "results": len(rows), "basis": basis}


def reading(s, site_auth):
    kd = s["diy_kd"]
    if kd is None:
        return ("beatable by page type: several weak or off-type results" if s["weak_results"] >= 3
                else "not estimated: add rd or auth per result (authority.py, Bing Webmaster, a backlink tool)")
    if s["weak_results"] >= 3:
        hint = "beatable: several weak or off-type results in the top 10"
    elif kd < 20:
        hint = "winnable for a young domain"
    elif kd < 40:
        hint = "possible with a strong page and some links"
    elif kd < 60:
        hint = "needs links; worth it only when the click is valuable"
    else:
        hint = "big-brand territory; skip unless value is very high"
    if site_auth is not None and s["median_auth"] is not None and s["median_auth"] - site_auth > 30:
        hint += f"; ranking domains are ~{s['median_auth'] - site_auth:.0f} points stronger than the site"
    return hint


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv")
    ap.add_argument("--site-auth", type=float, help="the site's own authority proxy, same scale as auth")
    ap.add_argument("--json")
    args = ap.parse_args()
    groups = collections.OrderedDict()
    with open(args.csv, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            groups.setdefault(r["term"].strip(), []).append(r)
    out = {}
    print("| term | DIY KD | median RD | median auth | brands | weak | features | reading |\n|---|---|---|---|---|---|---|---|")
    for term, rows in groups.items():
        s = score(rows)
        s["reading"] = reading(s, args.site_auth)
        out[term] = s
        print(f"| {term} | {s['diy_kd'] if s['diy_kd'] is not None else 'n/a'} | {s['median_rd'] if s['median_rd'] is not None else '-'} | "
              f"{s['median_auth'] if s['median_auth'] is not None else '-'} | {s['brands']} | {s['weak_results']} | "
              f"{' '.join(s['features']) or '-'} | {s['reading']} ({s['basis']}) |")
    print("\nDIY KD is an estimate from the visible results, not a vendor's KD. Label it as such.")
    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)


if __name__ == "__main__":
    main()
