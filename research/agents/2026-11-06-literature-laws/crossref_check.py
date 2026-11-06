import json, sys, time, urllib.parse, urllib.request
refs = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
out = []
for r in refs:
    q = urllib.parse.quote(r)
    url = f"https://api.crossref.org/works?query.bibliographic={q}&rows=2&select=DOI,title,issued,container-title,author"
    req = urllib.request.Request(url, headers={"User-Agent": "research-lit-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as f:
            items = json.load(f)["message"]["items"]
    except Exception as e:
        items = []; print("ERR", r[:60], e, file=sys.stderr)
    best = items[0] if items else {}
    t = (best.get("title") or [""])[0]
    y = (best.get("issued", {}).get("date-parts") or [[None]])[0][0]
    j = (best.get("container-title") or [""])[0]
    a = ", ".join(x.get("family", "") for x in (best.get("author") or [])[:4])
    out.append({"ref": r, "doi": best.get("DOI"), "title": t, "year": y, "journal": j, "authors": a})
    print(f"{y} | {a} | {t[:95]} | {j[:40]} | {best.get('DOI')}")
    time.sleep(1.3)
json.dump(out, open(sys.argv[2], "w"), indent=1)
