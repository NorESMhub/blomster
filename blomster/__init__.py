# blomster/__init__.py

# Expose submodules so users can do `import blomster.analysis`
from . import analysis, climatology, grid, plots, timeseries

# Expose analysis functions from the main package level
from .analysis import (
    deep_ocean_mask,
    load_ocean_grid,
    mean_at_depth,
    shared_quantile_levels,
    surface,
    symmetric_quantile_levels,
)

# Expose the BLOM grid loader
from .grid import load

# Expose plotting functions
from .plots import plot_map2d

# Define what gets imported when someone runs `from blomster import *`
__all__ = [
    "analysis",
    "climatology",
    "deep_ocean_mask",
    "grid",
    "load",
    "load_ocean_grid",
    "mean_at_depth",
    "plot_map2d",
    "plots",
    "shared_quantile_levels",
    "surface",
    "symmetric_quantile_levels",
    "timeseries",
]
