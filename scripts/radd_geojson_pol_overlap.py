## Libraries ##
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import rasterio
from rasterio.windows import Window
from rasterio.features import shapes
from shapely.geometry import shape
import numpy as np
import fiona
import glob


## Files ##
# Progreso
# path
farms_filepath = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
# file
farms_gdf = gpd.read_file(farms_filepath)
farms_gdf.info()

farms_gdf.plot()
plt.title('Colombia farms')
plt.show()

                    # first_feature_properties = farms_gdf.iloc[0].to_dict()
                    # first_feature_properties

# RADD
# path
radd_filepath = "data/download/RADD.geojson"
# file
radd_gdf = gpd.read_file(radd_filepath)
radd_gdf.info()
radd_gdf.crs == farms_gdf.crs
# Same coordinate system

radd_gdf.columns

radd_gdf.plot()
plt.title('RADD alerts (all available)')
plt.show()
### Observations: ###
# Here, all the areas monitored by RADD are displayed as tiles
# Let's filter what we are interested on


## Process geodataframes to our needs ##
# RADD
# Filter for South America only
# Define geographic bounds of South America (approximate)
south_america_bounds = {
    "north": 13.0,  # Northern limit
    "south": -56.0, # Southern limit
    "west": -82.0,  # Western limit
    "east": -34.0   # Eastern limit
}

# Use the bounds to filter
radd_gdf_f = radd_gdf.cx[south_america_bounds["west"]:south_america_bounds["east"],
                      south_america_bounds["south"]:south_america_bounds["north"]]

radd_gdf_f.head()
# cx allows for slicing based on geographical coordinates

radd_gdf_f.plot()
plt.title('RADD alerts for South America')
plt.show()

# Display the properties of the second feature
ex_feature_properties = radd_gdf_f.iloc[1].to_dict()
ex_feature_properties
### Observations: ###
# We notice that the first polygon is a square, compliant to the RADD description info
# In this "collective" geodataframe, there is no detailed info on values (to distinguish alerts), dates etc
# We only see a link for the individual tiles, whice we will be using later
# Concluding, we expect that the overlap with the whole geodataframe will not be meaningful,
# as a large part of SA is covered by the geodataframe


## Check overlap ##
check_overlap = gpd.sjoin(farms_gdf, radd_gdf_f, how="inner", op='intersects')
check_overlap
### Observations: ###
# method 'intersects' returns a df with 42 rows - which is the same as the farm's - as expected
# method 'overlaps' returns an empty df because all of the farm's polygons are included inside the RADD polygons

# Let's proceed with picking individual tiles


## Get into the detailed data ##
# by pulling the individual tif files from the web

# Trying to understand the data
# 00N_080W 
# selecting appr an area close to the colombian farms polygons

# Path to the GeoTIFF file
file_path = 'data\\download\\00N_080W.tif'

# Open the raster file
with rasterio.open(file_path) as src:
    # Check if the dataset is tiled
    if src.is_tiled:
        # Retrieve tile sizes (there could be different sizes for different bands)
        tile_sizes = src.block_shapes
        print("Tile sizes (rows x columns):", tile_sizes)
    else:
        print("The dataset is not tiled.")

# How many tiles?
with rasterio.open(file_path) as src:
    # Get the width and height of the raster dataset
    width = src.width
    height = src.height

    # Get the block sizes (tile sizes)
    block_width, block_height = src.block_shapes[0]  # Assuming all bands have the same block shape

    # Calculate the number of tiles in each dimension
    num_tiles_x = (width + block_width - 1) // block_width
    num_tiles_y = (height + block_height - 1) // block_height

    # Calculate the total number of tiles
    total_tiles = num_tiles_x * num_tiles_y

print("Number of tiles in X direction:", num_tiles_x)
print("Number of tiles in Y direction:", num_tiles_y)
print("Total number of tiles:", total_tiles)
### Observations: ###
# We notice that the amount of tiles is large and the size of each tile also
# This is consistent with the RADD description where it is mentioned that the 
# alerts detect changes with a spatial resolution of 10m
# We expect that any reading/processing of the file should take place in batches


## Process tiff file ##
# Read in windows 
chunk_size = 10000

# To time the reading of the file
import time
start_time = time.time()

# Open the GeoTIFF file
src = rasterio.open(file_path)
# Calculate the size of each chunk
width, height = src.width, src.height
    
all_geometries = []
    
# Iterate over each chunk
for i in range(0, height, chunk_size):
    for j in range(0, width, chunk_size):
        # Define the window for the current chunk
        window = Window(j, i, chunk_size, chunk_size)
        # Read current chunk
        image = src.read(1, window=window)
        # Check if the image slice is empty or all zeros
        if np.all(image == 0):
            print(f"Chunk at ({i},{j}) is all zeros or empty.")
            continue
        ## Process the current chunk
        # Create a mask with non-zero values: to filter the alerts
        mask = image != 0
        # Extract shapes from the mask
        transform = rasterio.windows.transform(window, src.transform)
        results = shapes(image, mask=mask, transform=transform)
        # Check the output from generator
        results_list = list(results)
        if not results_list:
            print(f"No valid shapes in chunk at ({i},{j}).")
            continue
        # Create polygons from the shapes
        chunk_geometries = [shape(geom) for geom, value in results_list if value > 0]
        # Append the results
        all_geometries.extend(chunk_geometries)

print("Reading of the file in chunks took --- %s seconds ---" % (time.time() - start_time))


# Create a geodataframe
start_time = time.time()
if all_geometries:
    gdf = gpd.GeoDataFrame({'geometry': all_geometries}, crs=src.crs)
else:
    print("No geometries were created from the raster data.")

print("Turning the tiff file to a geodataframe --- %s seconds ---" % (time.time() - start_time))

gdf.info()
gdf.head()[0]

gdf.plot()
plt.show()
### Observations: ###
# Reading the file in chunks took ~20mins
# When turning it into a geodataframe, info shows that we have ~20M rows
# So, it is next to impossible to plot it (at least as such)
# Also, we expect that the writing will take an awful lot of time so, will write in in chunks

## Save the geodataframe to a file 
# First, write to individual files

# Define the output directory and base file name
start_time = time.time()
output_dir = 'data/download/output/00N_080W_output_chunks'
base_filename = 'output_chunk_'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define the chunk size
chunk_size = 100000 # Large chuck size to fulfil operation

# Save the GeoDataFrame to Geopackage in chunks
for i, chunk_start in enumerate(range(0, len(gdf), chunk_size)):
    chunk_end = min(chunk_start + chunk_size, len(gdf))
    chunk = gdf.iloc[chunk_start:chunk_end]
    output_file = os.path.join(output_dir, f"{base_filename}{i}.gpkg")
    chunk.to_file(output_file, driver='GPKG')
print("Writing the chunks to individual files took --- %s seconds ---" % (time.time() - start_time))
### Observations: ###
# Producing these outputs took >1h, 190 files produced

# Now, merge the files
# Define schema for the output file
input_file = 'data/download/output/00N_080W_output_chunks/output_chunk_3.gpkg'
with fiona.open(input_file, 'r', driver='GPKG') as src:
    # Get the schema of the input file
    schema = src.schema
    schema
# schema = {'geometry': 'Polygon', 'properties': {}}


start_time = time.time()
# List of produced files
input_files = glob.glob(os.path.join(output_dir, '*.gpkg'))
# File to merge all the produced files
output_file = 'data/download/output/00N_080W_merged_output.gpkg'

# Open the output Geopackage file for writing
with fiona.open(output_file, 'w', driver='GPKG', schema = schema) as output:
    # Iterate over each input Geopackage file
    for input_file in input_files:
        if os.path.exists(input_file) and os.path.getsize(input_file) > 0:
        # Open the input Geopackage file for reading
            with fiona.open(input_file, 'r', driver='GPKG') as src:
                schema = src.schema
                #print(schema)
            # Iterate over each feature in the input file and write it to the output file
                for feature in src:
                    output.write(feature)
        else:
            print(f"Skipping empty or non-existent file: {input_file}")
print("Writing the produced individual files to one geopackage file took --- %s seconds ---" % (time.time() - start_time))


# Read the output
start_time = time.time()
merged_output = gpd.read_file(output_file)
print("Reading the partial merged geopackage file took --- %s seconds ---" % (time.time() - start_time))

merged_output.head()
merged_output.plot()
plt.show()

# # Remove the intermediate chunk files
for filename in os.listdir(output_dir):
    os.remove(os.path.join(output_dir, filename))


# Remove the empty output directory
# os.rmdir(output_dir)




## Check overlap ##
check_overlap = gpd.sjoin(farms_gdf, gdf, how="inner", op='intersects')










