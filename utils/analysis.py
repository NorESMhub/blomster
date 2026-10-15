import xarray as xr
import numpy as np


def surface():
    import numpy as np
    import xarray as xr
    """
    Load 2D field

    Args:
        arg1: 

    Returns:
        tuple: 
    """

    return 

def load_ocean_grid(grid_file):
    """
    load ocean grid data from BLOM grid file.
    for profile,depth,area,ocean mask,lat,lon are needed.
    """
    with xr.open_dataset(grid_file) as grid:
        return xr.Dataset(
            {
                "lat": grid["plat"].load(),
                "lon": grid["plon"].load(),
                "area": grid["parea"].load(),
                "depth_bottom": grid["pdepth"].load(),
                "ocean": (grid["pmask"] > 0).load(),
            }
        )


def mean_at_depth(variable,files,depth):
    fields = []
    for i, file in enumerate(files, 1):
        time_coder = xr.coders.CFDatetimeCoder(use_cftime=True)
        with xr.open_dataset(file,decode_times=time_coder) as ds:
            field = (
                ds[variable]
                .sel(depth=depth, method="nearest")
                .squeeze()
                .load()
            )
            fields.append(field)
            
    return xr.concat(fields, dim="year").mean("year")

def deep_ocean_mask(
    grid,
    lat_min=65.0,
    lat_max=90.0,
    bottom_depth_min=500.0,
    lon_min=None,
    lon_max=None,
):
    """create a mask for deep ocean region"""
    mask = (
        grid["ocean"]
        & (grid["lat"] >= lat_min)
        & (grid["lat"] <= lat_max)
        & (grid["depth_bottom"] > bottom_depth_min)
    )

    if lon_min is not None and lon_max is not None:
        lon = ((grid["lon"] + 180) % 360) - 180
        if lon_min <= lon_max:
            mask = mask & (lon >= lon_min) & (lon <= lon_max)
        else:
            mask = mask & ((lon >= lon_min) | (lon <= lon_max))

    return mask.rename("region_mask")

def shared_quantile_levels(
    data_list,
    qmin=0.001,
    qmax=0.999,
    nlevels=21,
):
    lower = []
    upper = []

    for data in data_list:
        q = data.quantile(
            [qmin, qmax],
            dim=None,
            skipna=True,
        ).values

        lower.append(float(q[0]))
        upper.append(float(q[1]))

    vmin = min(lower)
    vmax = max(upper)

    return np.linspace(vmin, vmax, nlevels)

def symmetric_quantile_levels(
    data,
    quantile=0.999,
    nlevels=21,
):
    vmax = float(
        abs(data).quantile(
            quantile,
            dim=None,
            skipna=True,
        )
    )

    return np.linspace(-vmax, vmax, nlevels)