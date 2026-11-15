# New architecture: the work refiled by the question it answers (2026-11-15)

**Type:** recategorization, no market test. **Owner's ask:** "Recategorize all the work that's been done and let's start to prioritize what to do next … transfer what we already know into a new architecture with clear purposes and clear tests and new categories."

* **Read the result in [../MAP.md](../MAP.md)** (purpose, the seven questions, the queue) and **[../CATALOG.md](../CATALOG.md)** (every study).
* `catalog.py` is the source of truth: one line per study with its question, mechanism, evidence grade and next step. It writes `../CATALOG.md` and `out/catalog.json`.
* `figure.py` → `out/knowledge_map.png`.
* The classification is the auditor's reading of each logged verdict. To change a filing, edit `catalog.py` and re-run it.

```
python catalog.py && python figure.py
```
