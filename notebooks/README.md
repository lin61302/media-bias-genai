# Analysis notebooks

[01_dashboard_and_measures.ipynb](01_dashboard_and_measures.ipynb) is executed and includes its results. The [HTML copy](01_dashboard_and_measures.html) can be downloaded and opened in a browser. [Figures](../figures/) are exported as PNG and PDF; [tables](../data/analysis/) retain the calculated values.

From the repository root, create an environment and run:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-analysis.txt
.venv/bin/python scripts/run_notebook.py
```

Use Python 3.10 or later. The first run downloads only public aggregate files from the commit and SHA-256 pins in `data/analysis_snapshot.json`, then caches them in an ignored directory. Subsequent runs validate the cache. No API credentials, model inference, news text or project database access are used. Running updates the notebook outputs, HTML, figures and derived tables. The older October 29 summary script remains independent.
