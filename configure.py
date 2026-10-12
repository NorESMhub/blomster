import papermill as pm
from pathlib import Path
import sys
import yaml

# load recipe
with open('recipe.yml', 'r') as f:
    cfg = yaml.safe_load(f)

#try:
#    climo = cfg['variables']['models']['blom']['hy']['climo']
#except (KeyError, TypeError):
#    climo = None

# generate TOC
toc = {}
toc = {
    'format': 'jb-book',
    'root': 'index',
    'chapters': cfg['diagnostics']
}
with open('_toc.yml', 'w') as f:
    yaml.dump(toc, f, default_flow_style=False, sort_keys=False)


# prepare notebooks
notebooks = Path("notebooks")
pynbs = sorted([notebooks / "index.ipynb", *notebooks.glob("*/*.ipynb")])
pynbs = [
    p for p in pynbs
    if not p.name.startswith("intro")
    and not any(part.startswith(".") for part in p.parts)
]

for pynb in pynbs:
    out = pynb.relative_to(notebooks)
    out.parent.mkdir(parents=True, exist_ok=True)
    pm.execute_notebook(
        str(pynb),
        str(out),
        parameters=cfg['experiment'],
        prepare_only=True,
        log_level="ERROR",
    )

# save settings to a YAML file
settings = {}
settings = {
    "blomster": cfg["blomster"],
    "experiment": cfg["experiment"],
    "grids": cfg["grids"],
    "datasets": cfg["datasets"]
}

with open('settings.yml', "w") as f:
    yaml.dump(settings, f, default_flow_style=False, sort_keys=False)
