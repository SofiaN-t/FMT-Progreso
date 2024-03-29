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
with rasterio.open("C:\\Users\\user\\Documents\\EAE\\peru_decrease_2004_01_01_to_2023_01_01.asc") as src:
    # Read the raster data
    data = src.read(1) # Assuming it's a single-band raster

    # Get the available metadata -- from chatgpt code below
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

    # Get the geographic location of the pixel in row 10, column 15
    row = 10
    col = 15

    X, Y = transform * (col, row)

    # Get the NOT no data values
    # Get the no data value from the metadata
    nodata_value = src.nodatavals[0]  # Assuming we're working with the first band
    
    # Create a mask for values that are (not) "no data"
    valid_data_mask = data != nodata_value
    no_data_mask = data == nodata_value
    
    # Count (not) "no data" values
    valid_data_count = np.sum(valid_data_mask)
    no_data_count = np.sum(no_data_mask)
    no_data_count
    
    print(f'Number of valid data values in the first band: {valid_data_count}')
    
    # If you need to perform operations on just the valid data, you can use this mask
    # For example, calculating the mean value of valid data
    valid_data_mean = np.mean(data[valid_data_mask])
    
    print(f'Mean value of valid data in the first band: {valid_data_mean}')


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
