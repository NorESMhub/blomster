from tracemalloc import stop
import papermill as pm
from pathlib import Path
import sys
import yaml

# Load ----
with open('diagnostics.yml', 'r') as f:
    cfg = yaml.safe_load(f)

#try:
#    climo = cfg['variables']['models']['blom']['hy']['climo']
#except (KeyError, TypeError):
#    climo = None

# Generate Table of Contents (TOC) for Jupyter Book
toc = {}
toc['format'] = 'jb-book'
toc['root'] = 'index'
toc['chapters'] = cfg['diagnostics']
with open('_toc.yml', 'w') as f:
    yaml.dump(toc, f, default_flow_style=False, sort_keys=False)


notebooks = Path("notebooks")
pynbs = sorted([notebooks / "index.ipynb", *notebooks.glob("*/*.ipynb")])
pynbs = [
    p for p in pynbs
    if not p.name.startswith("intro")
    and not any(part.startswith(".") for part in p.parts)
]
#print(pynbs)

#sys.exit(0)

for pynb in pynbs:
    out = pynb.relative_to(notebooks)               # same as ${pynb/notebooks/.}
    out.parent.mkdir(parents=True, exist_ok=True)   # same as mkdir -p

    pm.execute_notebook(
        str(pynb),
        str(out),
        parameters=cfg['experiment'],
        prepare_only=True,
        log_level="ERROR",
    )
    