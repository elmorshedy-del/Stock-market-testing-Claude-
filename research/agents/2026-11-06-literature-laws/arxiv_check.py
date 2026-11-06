import sys, time, json, re, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
NS = {"a": "http://www.w3.org/2005/Atom"}
titles = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
res = []
for t in titles:
    words = re.sub(r"[^A-Za-z0-9 ]", " ", t).split()
    q = " AND ".join("ti:" + w for w in words if len(w) > 3)[:300]
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode({"search_query": q, "max_results": 2})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "research-lit-check/1.0"}), timeout=40) as f:
            root = ET.fromstring(f.read())
        e = root.find("a:entry", NS)
        if e is None: raise ValueError("no hit")
        rec = {"query": t, "id": e.find("a:id", NS).text.split("/abs/")[-1], "title": " ".join(e.find("a:title", NS).text.split()),
               "year": e.find("a:published", NS).text[:4], "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)][:5],
               "abstract": " ".join(e.find("a:summary", NS).text.split())}
    except Exception as ex:
        rec = {"query": t, "error": str(ex)}
    res.append(rec)
    print(rec.get("id"), "|", rec.get("year"), "|", rec.get("title", rec.get("error"))[:100])
    time.sleep(3.2)
json.dump(res, open(sys.argv[2], "w"), indent=1)
