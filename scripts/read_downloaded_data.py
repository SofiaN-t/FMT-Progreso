## Use a downloaded file from Global Forest Watch
# Read the GeoJSON file
import json
with open("data\\download\\Deforestation_alerts_(RADD).geojson") as f:
    data = json.load(f)

data # includes the full thing

# Extract polygons from the GeoJSON
from shapely.geometry import shape, Polygon
polygons = []
for feature in data['features']:
    polygon_geojson = feature['geometry']
    polygon = shape(polygon_geojson)
    polygons.append(polygon)

polygons # includes only the polygons

# Extract tile_id from the GeoJSON
tile_ids = []
for feature in data['features']:
    polygon_properties = feature['properties']
    tile_id=polygon_properties['tile_id']
    tile_ids.append(tile_id)
    # can also add shape length & shape area

tile_ids
len(tile_ids)


## Use a .tif file from Global Forest Watch
### DO NOT RUN until clear what is wrong!!
### Can overcome this by either disabling the size limit or exploding it
### Not going to do it until I research the reputation of the source more -- although reasonable to do

# # install first by running 'pip install Pillow'
# from PIL import Image

# # Open the .tif file
# image = Image.open("data\\download\\10N_090W.tif")

# # Display the image
# image.show()
### image decompression bomb error!! could be decompression bomb DOS attack


### Use a .asc file from https://www.arcgis.com/home/item.html?id=ffae4a5b46be4cdd8ce55486fe13df55
# install first
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import fiona
from fiona.crs import from_epsg
import numpy as np

# Open the raster file
## The file is not in data folder because of exceeding git limits
## Can remove from the git exchange
with rasterio.open("C:\\Users\\user\\Documents\\EAE\\peru_decrease_2004_01_01_to_2023_01_01.asc") as src:
    # Read the raster data
    data = src.read(1) # Assuming it's a single-band raster

    # Get the available metadata
    profile = src.profile
    oviews = src.overviews(1) # here, this is empty, hence the following line throws an error
    # oview=oviews[0]
    # Get the transform and shape of the raster
    transform = src.transform
    width = src.width
    height = src.height

    print(transform) 
    print(width)
    print(height)

    # Get the geographic location of the pixel in row 11, column 16
    row = 10
    col = 15

    X, Y = transform * (col, row)

    # Get the NOT no data values
    # Get the no data value from the metadata
    nodata_value = src.nodatavals[0]  # Assuming we're working with the first band
    
    # Create a mask for values that are not "no data"
    valid_data_mask = data != nodata_value
    # This returns an array of True/False
    unique_valid_values = np.unique(data[valid_data_mask])
    unique_valid_values
    # The unique values are 0,1,and what seems to be years from 2004 to 2023
    # consistent with the data description (at least when it comes to the years)


    # specific_value_mask = band1 == specific_value
    
    # # Create a masked array where non-matching values are set to NaN
    # masked_band1 = np.where(specific_value_mask, band1, np.nan)

    # Isolate the array with one of the unique values
    val_2023_mask = data == 2023
    arr_2023 = data[val_2023_mask]
    # This is a 1D array, without the geospatial information encoded in it.
    len(arr_2023) # 560

    # Dictionary to hold the indices of each unique valid value
    indices_of_unique_values = {}
    # Loop through each unique valid value to find its indices
    for value in unique_valid_values:
        # Find the indices where this value occurs
        indices = np.where(data == value)
        # Store the indices in the dictionary
        indices_of_unique_values[value] = indices

    indices_of_unique_values[2004]
    # How to interpret the output of this:
    # There are xyz pixels in the raster with the value 2004, located at:
    # row 4, col 2946
    # row 46, col 2805
    # ...    

    # To count the amount of elements within the arrays
    ind_val_2023 = indices_of_unique_values[2023]
    num_elements = len(ind_val_2023[0]) # 560 - obviously, the same for the second array
    # How do these compare against 2004?
    ind_val_2004 = indices_of_unique_values[2004]
    num_elements = len(ind_val_2004[0]) # 12157

    # Can we check whether there are combinations of rows and columns that overlap?
    indices_2022 = indices_of_unique_values[2022]  # This is a tuple of arrays (rows, cols)
    indices_2023 = ind_val_2023

    # Convert indices to sets of tuples
    set_of_coordinates_2022 = set(zip(indices_2022[0], indices_2022[1]))
    set_of_coordinates_2023 = set(zip(indices_2023[0], indices_2023[1]))

    # Find common elements between the two sets
    overlap = set_of_coordinates_2022.intersection(set_of_coordinates_2023)

    # Check if there is any overlap
    if overlap:
        print("There are overlapping row-column combinations.")
        print("Overlapping coordinates (row, column):", overlap)
    else:
        print("There are no overlapping row-column combinations.")

    # If you need to perform operations on just the valid data, you can use this mask
    # For example, calculating the mean value of valid data
    valid_data_mean = np.mean(data[valid_data_mask])
    print(f'Mean value of valid data in the first band: {valid_data_mean}')

            # # For the no-data values
            # no_data_mask = data == nodata_value
            
            # # Count (not) "no data" values
            # valid_data_count = np.sum(valid_data_mask)
            # no_data_count = np.sum(no_data_mask)
            # no_data_count
            
            # print(f'Number of valid data values in the first band: {valid_data_count}')
    

# Read, transfrom and nest again depedning on the data you are interested on
# Generate shapes from the raster data
geom = list(shapes(data, transform=transform))

# Convert the shapes to Shapely geometries
geometries = [shape(geom) for geom, _ in geom]
## when you print it, you get an extensive list

# Define the output shapefile schema
schema = {
    'geometry': 'Polygon',
    'properties': {'id': 'int'},
}

# Write the geometries to a shapefile
with fiona.open('data\download\output\output_peru04_23.shp', 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as output:
    for i, geometry in enumerate(geometries):
        output.write({
            'geometry': geometry,
            'properties': {'id': i+1},  # Assigning an ID to each feature
        })
### Takes a long time to run - forced stopping


## Convert a .tif to a geojson file
import rasterio
from rasterio.features import shapes
import json

# Open the GeoTIFF file
with rasterio.open("data\\download\\30N_120W.tif") as src:
    # Read the raster data
    data = src.read(1)  # Assuming it's a single-band raster
    ### arrays that show only 0
    ### Could get an --> 
    ### ArrayMemoryError:  Unable to allocate 18.6 GiB for an array with shape (1, 100000, 100000) and data type uint16
    ### Before you open it, try to understand what is within (below)

    # Get the transform
    transform = src.transform

    # Generate shapes from the raster data
    geom = list(shapes(data, transform=transform))

# Convert the shapes to GeoJSON features
features = [{"type": "Feature", "geometry": geom, "properties": {}} for geom, _ in geom]

# Create a GeoJSON object
geojson_obj = {"type": "FeatureCollection", "features": features}

# Write the GeoJSON object to a file
with open("data\download\output\output_30n_120w.geojson", "w") as output_file:
    json.dump(geojson_obj, output_file)
## Have not run yet


## Explore a .tif file
# Open the GeoTIFF file
with rasterio.open("data\\download\\30N_120W.tif") as src:
    # from # https://geohackweek.github.io/raster/04-workingwithrasters/

    profile = src.profile
    oviews = src.overviews(1) # here, this is empty, hence the following line throws an error
    # oview=oviews[0]

    ## These can be inferred from the profile
    # Check the data type
    data_type = src.dtypes[0]  # Assuming it's a single-band raster
    # Check the number of bands
    num_bands = src.count
    # Check the coordinate reference system (CRS)
    crs = src.crs


### Interesting read on tif files
# https://geohackweek.github.io/raster/04-workingwithrasters/
    

### Same file, different checks
# rasterio documentation: https://rasterio.readthedocs.io/en/stable/topics/reading.html
    
src = rasterio.open("data\\download\\30N_120W.tif")
array = src.read(1) # memory error now
array.shape


## What about subsets?
window = rasterio.windows.Window(1024, 1024, 1280, 2560)

src = rasterio.open("data\\download\\30N_120W.tif")
array = src.read(1, window=window)
array.shape

import matplotlib.pyplot as plt
# install first

plt.figure(figsize=(6,8.5))
plt.imshow(array)
plt.colorbar(shrink=0.5) # this is probably not needed
plt.show()
# not very enlightening


# ChatGPT 4
# Read an individual tile from the tif file
from PIL import TiffImagePlugin

# Since the TIFF file is tiled, we can attempt to read a single tile directly
# This requires low-level access to the TIFF file structure, which PIL supports

# Open the TIFF file in a mode that allows access to its internal structure
with TiffImagePlugin.AppendingTiffWriter("data/download/30N_120W.tif", True) as tf:
    # Access the TIFF file's IFD (Image File Directory) to get tile information
    ifd = TiffImagePlugin.ImageFileDirectory_v2()

    # Assuming the TIFF library and image supports it, load the IFD from the file
    ifd.load(tf)

    # Fetch the first tile. This involves getting the offset and byte count of the tile data
    # These are stored in tags 324 (TileOffsets) and 325 (TileByteCounts) respectively
    tile_offsets = ifd.tag_v2.get(324)  # TileOffsets
    tile_byte_counts = ifd.tag_v2.get(325)  # TileByteCounts

    # Read the first tile as an example
    if tile_offsets and tile_byte_counts:
        # Seek to the offset of the first tile
        tf.seek(tile_offsets[0])
        # Read the number of bytes specified for this tile
        tile_data = tf.read(tile_byte_counts[0])

        # Now we have the raw tile data, but note this is not yet a viewable image
        # To make it viewable, we would need to know the exact format and dimensions of the tile
        # For simplicity, let's just report success if we've gotten this far
        tile_read_success = True
    else:
        tile_read_success = False

tile_read_success, len(tile_data) if tile_read_success else "No tile data"
### Error when running this
### The error occurred because the method used to access the TIFF file's internal structure 
### wasn't suitable for reading data directly in this manner.


## Read the RADD file
import json

# Load the GeoJSON file as a Python dictionary
with open("data\download\Deforestation_alerts_(RADD).geojson", 'r') as file:
    alerts_data = json.load(file)

# Extract basic information about the file
info_alternative = {
    "Type": alerts_data.get("type"),
    "Number of Features": len(alerts_data.get("features", [])),
    "Example Feature": alerts_data.get("features", [{}])[0] if alerts_data.get("features", []) else "No features found"
}

info_alternative
## There doesn't seem to be dates in the available info

## Let's try to extract the properties with an alternative reading
import geopandas as gpd

# Load the GeoJSON file
alerts_path = 'data\download\Deforestation_alerts_(RADD).geojson'
alerts_gdf = gpd.read_file(alerts_path)

# Check the properties of the first feature
first_feature_properties = alerts_gdf.iloc[0].to_dict()
second_feature_properties = alerts_gdf.iloc[1].to_dict()
last_feature_properties = alerts_gdf.iloc[70].to_dict()


# Print the properties to find out the names
for property_name, property_value in first_feature_properties.items():
    print(f"{property_name}: {property_value}")

for property_name in alerts_gdf.columns:
    sample_value = alerts_gdf[property_name].dropna().iloc[0]  # Get the first non-NA value
    print(f"{property_name}: {sample_value}")


## Let's proceed to extract the coordinates of the areas with the alerts
# Extracting the coordinates for each alert area
alert_coordinates = [feature['geometry']['coordinates'] for feature in alerts_data.get('features', [])]
## This output is a list of lists

# # For demonstration, let's just show the first alert's coordinates to keep the output concise
# first_alert_coordinates = alert_coordinates[0] if alert_coordinates else []

# first_alert_coordinates

## What about trying to extract the values?
nodata_value = alerts_data.nodatavals[0]
# This argument does not work with a geopandas file

# Let's try to read in the geojson file using the rasterio libray
src = rasterio.open("data\download\Deforestation_alerts_(RADD).geojson")
# Not possible
# radd_raster = src.read(1)


# Let's try to plot with geopandas
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
import geopandas as gpd

# Create GeoDataFrame from alert coordinates
# First, convert each set of coordinates into a Shapely Polygon
polygons = [Polygon(coords[0]) for coords in alert_coordinates if coords]  # Ensure non-empty
alerts_geo = gpd.GeoDataFrame(geometry=polygons)

# Plotting the map
fig, ax = plt.subplots(figsize=(10, 10))
alerts_geo.boundary.plot(ax=ax)
plt.title('Map of Alert Areas')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

#plt.savefig("data/download/output/radd_map.png")
plt.show()


# Let's try and plot the alert areas on a map of the earth
# install first
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# Create a new figure with a cartographic projection (PlateCarree is commonly used for world maps)
fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})

# Add map features
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEANS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Plot each alert polygon onto the map
for poly in polygons:
    ax.add_geometries([poly], crs=ccrs.PlateCarree(), edgecolor='red', facecolor='none')

# Set the extent of the map to a global scale
ax.set_global()

# Add gridlines and labels to the map
ax.gridlines(draw_labels=True)

plt.title('Deforestation Alert Areas on the World Map')
plt.savefig("data/download/output/radd_map_earth.png")
plt.show()

# # Let's do the same with zooming-in
# Create a new figure with a cartographic projection
fig, ax = plt.subplots(figsize=(20, 10), subplot_kw={'projection': ccrs.PlateCarree()})

# Add map features for better visualization
ax.add_feature(cfeature.LAND)
ax.add_feature(cfeature.OCEANS)
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS, linestyle=':')

# Plot each alert polygon onto the map
for poly in polygons:
    ax.add_geometries([poly], crs=ccrs.PlateCarree(), facecolor='red', edgecolor='black', alpha=0.5)

# Set the extent of the map to the bounds of our polygons for a focused view
# Calculating the min and max for latitude and longitude from all alerts
all_lons = [lon for polygon in polygons for lon in polygon.exterior.coords.xy[0]]
all_lats = [lat for polygon in polygons for lat in polygon.exterior.coords.xy[1]]
min_lon, max_lon, min_lat, max_lat = min(all_lons), max(all_lons), min(all_lats), max(all_lats)

# Add some margin to the extent
margin = 5
ax.set_extent([min_lon - margin, max_lon + margin, min_lat - margin, max_lat + margin], crs=ccrs.PlateCarree())

# Add gridlines for reference
ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

plt.title('Deforestation Alert Areas')
plt.savefig("data/download/output/radd_map_earth_zoom.png")
plt.show()
















#### DEPRECATED

# 1. When there are some incompatibilities between geopandas and plotting library
# # Let's do the same directly 
# from matplotlib.patches import Polygon as MplPolygon
# from matplotlib.collections import PatchCollection

# # Creating the plot
# fig, ax = plt.subplots(figsize=(10, 10))
# patches = []

# # Convert alert coordinates to matplotlib Polygons and add them to the plot
# for alert_coords in alert_coordinates:
#     for poly_coords in alert_coords:  # Handle potentially multiple polygons per alert
#         poly = MplPolygon(poly_coords, closed=True, edgecolor='r', facecolor='none')
#         patches.append(poly)

# # Add patches to the axes
# p = PatchCollection(patches, match_original=True)
# ax.add_collection(p)

# # Setting the plot limits to the first alert's bounds as an example
# # Ideally, you would set this dynamically based on all alerts' extents
# x_min, y_min, x_max, y_max = patches[0].get_extents().bounds
# ax.set_xlim(x_min, x_max)
# ax.set_ylim(y_min, y_max)

# plt.title('Map of Alert Areas')
# plt.xlabel('Longitude')
# plt.ylabel('Latitude')
# plt.show()


