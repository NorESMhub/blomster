import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.path as mpath

def plot_map2d(lon, lat, var, proj='PlateCarree', norm=None, cmap=mpl.colormaps['viridis']):
    """
    Plot 2D map with a north pole view.

    Args:
        lon (np.ndarray): Longitudes.
        lat (np.ndarray): Latitudes.
        var (np.ndarray): Variable data to plot.
        levels (list or np.ndarray): Discrete levels for color normalization.
        cmap_name (str): Name of the colormap.
        figfile (str): Output file name for saving the plot.
    """

    # Create the map
    #proj = ccrs.NearsidePerspective(central_longitude=0.0, central_latitude=80.0, satellite_height=3e6)
    if proj == 'PlateCarree':
        proj = ccrs.PlateCarree(central_longitude=90.0)
    elif proj == 'NearsidePerspective':
        proj = ccrs.NearsidePerspective(central_longitude=0.0, central_latitude=80.0, satellite_height=3e6)
    else:
        print("Unknown projection type. Use PlateCarree instead.")
        proj = ccrs.PlateCarree(central_longitude=90.0)

    fig, ax = plt.subplots(1, figsize=(11.7, 8.3), dpi=96, subplot_kw={"projection": proj})

    # Plot the mesh
    pm = ax.pcolormesh(lon, lat, var, cmap=cmap, norm=norm,
                       transform=ccrs.PlateCarree(), shading='auto', rasterized=True)

    # Add map features
    #ax.stock_img()
    ax.add_feature(cfeature.LAND, facecolor='lightgray')

    gl = ax.gridlines(ylocs=range(-90, 90, 30), draw_labels=True)
    gl.ylocator = mpl.ticker.FixedLocator(range(-90,90,30))

    # Add colorbar
    cb = plt.colorbar(pm, ax=ax, fraction=0.2, shrink=0.4, label='[yr]')
    cb.set_label(label=var.units, size=14)
    cb.ax.tick_params(labelsize=12)

    return fig, ax


def plot_arctic_maps(
    lon,
    lat,
    settings,
    titles,
    suptitle=None,
    figsize=None,
    extent=(-180, 180, 60, 90),
    layout='horizontal',
):
    """
    NorthPolarStereo
    (data, levels, cmap_name, colorbar_label)
    """

    projection = ccrs.NorthPolarStereo(central_longitude=0)
    data_crs = ccrs.PlateCarree()

    nplots = len(settings)
    if layout == "horizontal":
        nrows = 1
        ncols = nplots

        if figsize is None:
            figsize = (6 * nplots, 5.5)

    elif layout == "vertical":
        nrows = nplots
        ncols = 1

        if figsize is None:
            figsize = (6, 5.5 * nplots)
    else:
        raise ValueError("layout must be 'horizontal' or 'vertical'")

    fig, axes = plt.subplots(nrows,ncols,figsize=figsize,subplot_kw={"projection": projection},squeeze=False,)
    axes = axes.ravel()
    theta = np.linspace(0, 2 * np.pi, 200)
    circle = mpath.Path(
        np.column_stack([
            0.5 + 0.5 * np.cos(theta),
            0.5 + 0.5 * np.sin(theta),
        ])
    )

    for ax, setting, title in zip(axes, settings, titles):

        data, levels, cmap_name, cbar_label = setting

        cmap = mpl.colormaps[cmap_name]
        norm = mpl.colors.BoundaryNorm(levels,ncolors=cmap.N,clip=False,)
        plot = ax.pcolormesh(
            lon,
            lat,
            data,
            cmap=cmap,
            norm=norm,
            transform=data_crs,
            shading="auto",
        )

        ax.set_extent(extent, crs=data_crs)
        ax.set_boundary(circle, transform=ax.transAxes)

        ax.add_feature(
            cfeature.LAND,
            facecolor="0.75",
            edgecolor="0.35",
            linewidth=0.4,
            zorder=3,
        )

        ax.coastlines(
            resolution="50m",
            linewidth=0.45,
        )

        ax.gridlines(
            crs=data_crs,
            xlocs=np.arange(-180, 181, 30),
            ylocs=np.arange(60, 91, 10),
            linewidth=0.35,
            color="0.5",
            alpha=0.6,
        )

        ax.set_title(title)

        fig.colorbar(
            plot,
            ax=ax,
            label=cbar_label,
            shrink=0.78,
            pad=0.06,
            format="%.1f"
        )

    if suptitle is not None:
        fig.suptitle(
            suptitle,
            fontsize=10,
            y=0.98,
        )

    fig.subplots_adjust(
        top=0.92,
        hspace=0.25,
    )

    return fig, axes
