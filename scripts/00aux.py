import streamlit as st
import os
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds

# Compare loading raster functions
# To load raster data (based on window)
def read_geotiff_window_upd(file_path, bounds):
    with rasterio.open(file_path) as src:
        # Convert geographic to pixel coordinates
        window = from_bounds(*bounds, src.transform)
        # Read the window
        data = src.read(1, window=window)
        if only_alerts == True:
            # Keep only alerts (non-negative values)
            data = np.where(data > 0, data, np.nan)
        else:
            data = data
        # Get the transform of window to be able to map pixel to geographic
        transform = src.window_transform(window)
        return data, transform 

with rasterio.open(tif_path) as src:
    window = from_bounds(*bounds, src.transform)
    # Read the window
    data = src.read(1, window=window)
    # Keep only alerts (positive values)
    data_f = np.where(data > 0, data, np.nan)
    # Get the transform of window to be able to map pixel to geographic
    transform = src.window_transform(window)

import numpy as np
np.where()


tif_path='data/input/raw/10N_080W.tif'
bounds = (-76.5, 1.8, -75.5, 2) # (min_lon, min_lat, max_lon, max_lat)
tif_data, tif_transform = read_geotiff_window_upd(tif_path, bounds)
tif_data
tif_data.shape
tif_transform


def read_radd(file_path, bounds):
    with rasterio.open(file_path) as src:
    # rasterio library to read raster data
    # the file is large, therefore reading and visualising as a whole will not work
    # we zoom in an area of interest, and in order to make sure that it worked, we visualise it

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

lat_range = [1.8, 2]  # y-axis
lon_range = [-76.5, -75.5]


with rasterio.open(tif_path) as src:

    # Transform geographic coordinates into raster coordinates
    top_left = src.index(lon_range[0], lat_range[1])
    bottom_right = src.index(lon_range[1], lat_range[0])

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

