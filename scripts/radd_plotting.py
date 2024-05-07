## Functions ##
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.plot import show
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt

# To read a specific window of the RADD data
def display_area(raster_path, vector_path, lat_range, lon_range, only_alerts):
    with rasterio.open(raster_path) as src:
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
    gdf = gpd.read_file(vector_path)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('white') #background

    # Calculate non-nan min and max
    valid_data = masked_image[~np.isnan(masked_image)]
    vmin, vmax = valid_data.min(), valid_data.max()

    show(masked_image, transform=transform, ax=ax, cmap='viridis', vmin=vmin, vmax=vmax, alpha=0.5, extent=bounds) 
    gdf.to_crs(src.crs).plot(ax=ax, facecolor='none', edgecolor='red', linewidth = 2, label = 'Farms polygons')  # Overlay polygons
    # Create a custom legend
    legend_elements = [
    Line2D([0], [0], color='w', lw=2, label='RADD alerts'),
    Line2D([0], [0], color='red', lw=2, label='Coffee farms')
    ]

    ax.legend(handles=legend_elements, title="")
    plt.show()


def display_image_with_polygons(raster_path, vector_path, lat_range, lon_range):
    with rasterio.open(raster_path) as src:
        # Transform geographic coordinates to the image's raster coordinates
        # Ensure coordinates are within the bounds of the raster
        transform = src.transform
        width, height = src.width, src.height

        # Calculate pixel coordinates of the bounding box
        top_left = src.index(lon_range[0], lat_range[1])
        bottom_right = src.index(lon_range[1], lat_range[0])

        # Ensure coordinates are within bounds
        top_left = (max(0, min(top_left[0], height - 1)), max(0, min(top_left[1], width - 1)))
        bottom_right = (max(0, min(bottom_right[0], height - 1)), max(0, min(bottom_right[1], width - 1)))

        # Calculate window based on the bounded coordinates
        window = rasterio.windows.Window.from_slices(
            (min(top_left[0], bottom_right[0]), max(top_left[0], bottom_right[0])),
            (min(top_left[1], bottom_right[1]), max(top_left[1], bottom_right[1]))
        )

        # Read the data within the defined window
        data = src.read(1, window=window)

        # Convert window bounds to geographic coordinates
        bounds = src.window_bounds(window)

    # Apply a mask to the data
    masked_data = np.where(data > 0, data, np.nan)  # Replace negative values with np.nan

    gdf = gpd.read_file(vector_path)

    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_facecolor('white')

    # Display the masked data with adjusted extent to match geographic coordinates
    show(masked_data, transform=src.window_transform(window), ax=ax, cmap='viridis', alpha=0.5, extent=bounds)

    # Plotting polygons
    gdf.to_crs(src.crs).plot(ax=ax, facecolor='none', edgecolor='red', linewidth=2)

    plt.show()




## Plot ##
# By calling the function
raster_path = 'data\\download\\10N_080W.tif'
vector_path = 'data\\raw\\output\\Polygons_EAE_project_Progreso.geojson'
lat_range = [1.8, 2]  # y-axis
lon_range = [-76.5, -75.5]  # x-axis
only_alerts = False # boolean to know whether alerts or not
display_area(raster_path,  vector_path, lat_range, lon_range, only_alerts)
display_image_with_polygons(raster_path, vector_path, lat_range, lon_range)