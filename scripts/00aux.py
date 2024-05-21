import streamlit as st
import os
import geopandas as gpd
import rasterio
from rasterio.windows import from_bounds
from rasterio.warp import transform_bounds
from shapely.geometry import box
from rasterio.features import shapes
from shapely.geometry import shape, mapping, Polygon
import geojson


# Raster to geojson -- Check another method

# Define the bounding box (longitude and latitude)
min_lon, min_lat = -76.5, 1.8
max_lon, max_lat = -75.5, 2


# Open the .tif file
tif_path = 'data\\input\\raw\\10N_080W.tif'
with rasterio.open(tif_path) as src:
    # Transform bounding box coordinates to the coordinate reference system of the .tif
    bounds = [min_lon, min_lat, max_lon, max_lat]
    window = from_bounds(*bounds, transform=src.transform)
    
    # Read the window of data
    data = src.read(1, window=window)
    
    # Get the affine transform for the window
    transform = src.window_transform(window)

# Create a list of polygons with their values
features = []
for j in range(data.shape[0]):
    for i in range(data.shape[1]):
        value = data[j, i]
        #if value > 0:  # Retain only positive values
        x, y = transform * (i, j)
        polygon = Polygon([
            (x, y),
            (x + transform.a, y),
            (x + transform.a, y + transform.e),
            (x, y + transform.e),
            (x, y)
        ])
        feature = geojson.Feature(geometry=mapping(polygon), properties={"value": int(value)})
        features.append(feature)

# Create a GeoJSON FeatureCollection
feature_collection = geojson.FeatureCollection(features)

# Save the GeoJSON to a file
geojson_path = 'data\\input\\processed\\radd_gdf_from_feature_collection.geojson'
with open(geojson_path, 'w') as f:
    geojson.dump(feature_collection, f)

# 
radd_gdf = gpd.read_file(geojson_path)

# Plot the GeoDataFrame
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(10, 10))
radd_gdf.plot(ax=ax, column='value', cmap='viridis', legend=True)

# Customize the plot
ax.set_title('GeoJSON Data')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

# Show the plot
plt.show()




# Raster to geojson -- Retains values but I don't trust it
# Load raster data
with rasterio.open('path_to_your_raster.tif') as src:
    image = src.read(1)  # Read the first band
    mask = image != 0    # Create a mask for non-zero values
    results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) in enumerate(
            shapes(image, mask=mask, transform=src.transform))
    )

# Convert to GeoDataFrame
geoms = list(results)
gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)

# Optionally reproject to WGS84
gdf = gdf.to_crs('EPSG:4326')




# Convert raster to geojson -- Does not retain values
plots_path = "data\\input\\processed\\plots_colombia.geojson"
# file
plots_gdf = gpd.read_file(plots_path)
print(plots_gdf.crs)


radd_path = 'data/input/raw/10N_080W.tif'
lat_range = [1.8, 2]  # y-axis
lon_range = [-76.5, -75.5]

with rasterio.open(radd_path) as src:
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

    # Get the crs of the raster
    coord_sys = src.crs 

    # Read the data within the window
    image = src.read(window=window)

    # Get the transformation for the window
    transform = src.window_transform(window)

    # Convert window bounds to geographic coordinates
    bounds = src.window_bounds(window)

    # To keep the values
    results = (
        {'properties': {'raster_val': v}, 'geometry': s}
        for i, (s, v) in enumerate(
            shapes(image, transform=src.transform)) #mask=mask, 
    )

# Convert to GeoDataFrame
geoms = list(results)
radd_gdf = gpd.GeoDataFrame.from_features(geoms, crs=src.crs)
radd_gdf.head()
radd_gdf.to_file('data\\input\\processed\\radd_gdf.geojson', driver='GeoJSON') 

# # Unpack the bounds
# minx, miny, maxx, maxy = bounds

# if coord_sys != plots_gdf.crs:
#     minx, miny, maxx, maxy = transform_bounds(coord_sys, plots_gdf.crs, minx, miny, maxx, maxy)


# # Create a bounding box in geographic coordinates
# bbox = box(minx, miny, maxx, maxy)





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

