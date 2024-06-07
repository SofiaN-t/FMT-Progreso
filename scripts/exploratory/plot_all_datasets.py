## Functions ##
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.plot import show
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt


# Function to plot all areas
def display_areas(radd_path, plots_path, amaz_path, lat_range, lon_range, only_alerts):
    with rasterio.open(radd_path) as src:
        # Transform geographic coordinates into raster coordinates
        top_left = src.index(lon_range[0], lat_range[1])
        bottom_right = src.index(lon_range[1], lat_range[0])

        # Calculate the window to read based on the raster coordinates
        window = rasterio.windows.Window.from_slices(
            (min(top_left[0], bottom_right[0]), max(top_left[0], bottom_right[0])),
            (min(top_left[1], bottom_right[1]), max(top_left[1], bottom_right[1]))
        )

        # Read the data within the window
        image = src.read(window=window)

        # Get the transformation for the window
        transform = src.window_transform(window)

        # Convert window bounds to geographic coordinates
        bounds = src.window_bounds(window)

    # Apply a mask to the data (if triggered)
    if only_alerts == True:
        masked_image = np.where(image > 0, image, np.nan)  # Replace negative values with np.nan
    else:
        masked_image = image

    # Load the farms polygons
    plots_gdf = gpd.read_file(plots_path)

    # Load & process the amazonian colombian polygons
    amaz_gdf = gpd.read_file(amaz_path)
    amaz_gdf = amaz_gdf.explode(index_parts=True)
    amaz_gdf = amaz_gdf.loc[amaz_gdf['deforestac'] == 'Perdida']

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('white') #background

    # Calculate non-nan min and max
    valid_data = masked_image[~np.isnan(masked_image)]
    vmin, vmax = valid_data.min(), valid_data.max()

    show(masked_image, transform=transform, ax=ax, cmap='viridis', vmin=vmin, vmax=vmax, alpha=0.5, extent=bounds) 
    plots_gdf.to_crs(src.crs).plot(ax=ax, facecolor='none', edgecolor='red', linewidth = 2, label = 'Farms polygons')
    amaz_gdf.to_crs(src.crs).plot(ax=ax, facecolor='none', edgecolor='black', linewidth=2, label='Amazonian Colombia')

    # Manually set the bounds of the plot to the bounds of the raster data
    ax.set_xlim(lon_range)
    ax.set_ylim(lat_range)

    # Create a custom legend
    legend_elements = [
    Line2D([0], [0], color='w', lw=2, label='RADD'),
    Line2D([0], [0], color='red', lw=2, label='Coffee farms'),
    Line2D([0], [0], color='black', lw=2, label='Amazonian')
    ]

    ax.legend(handles=legend_elements, title="")
    plt.title('RADD alerts, Amazonian alerts & farms polygons within area of interest')
    plt.show()


## Plot ##
# By calling the function
radd_path = 'data\\input\\raw\\10N_080W.tif'
plots_path = 'data\\input\\processed\\plots_colombia.geojson'
amaz_path = "data\\input\\raw\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp"

lat_range = [1.8, 2]  # y-axis
lon_range = [-76.5, -75.5]  # x-axis
only_alerts = False # boolean to know whether to plot only alerts

display_areas(radd_path,  plots_path, amaz_path, lat_range, lon_range, only_alerts)
# When you do not see any of the datasets, the limits of the plot probably do not include those