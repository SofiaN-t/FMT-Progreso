## Libraries ##
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import numpy as np
import os



## Read files ##
# Progreso
# path
farms_filepath = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
# file
farms_gdf = gpd.read_file(farms_filepath)
farms_gdf.info()

farms_gdf.plot()
plt.show()

first_feature_properties = farms_gdf.iloc[0].to_dict()
first_feature_properties

# RADD
# path
radd_filepath = "data/download/RADD.geojson"
# file
radd_gdf = gpd.read_file(radd_filepath)
radd_gdf.info()
radd_gdf.crs == farms_gdf.crs
# Same coordinate system

radd_gdf.plot()
plt.show()

radd_gdf.columns
radd_gdf.values

# first_feature_properties = radd_gdf.iloc[0].to_dict()
# first_feature_properties

## Intermezzo ##
# To check explore
                    # import geodatasets

                    # df = gpd.read_file(geodatasets.get_path("geoda.chicago_health"))
                    # df.head()
                    # df.columns
                    # explore_df=df.explore("community", cmap="Blues")
                    # output_file = "example_community.html"
                    # explore_df.save(output_file)

                    # import webbrowser
                    # webbrowser.open(output_file, new=2) 


# Filter for South America only
# Define geographic bounds of South America (approximate)
south_america_bounds = {
    "north": 13.0,  # Northern limit
    "south": -56.0, # Southern limit
    "west": -82.0,  # Western limit
    "east": -34.0   # Eastern limit
}

# Use the bounds to filter the GeoDataFrame
radd_gdf_f = radd_gdf.cx[south_america_bounds["west"]:south_america_bounds["east"],
                      south_america_bounds["south"]:south_america_bounds["north"]]

radd_gdf_f.head()
# cx allows for slicing based on geographical coordinates

radd_gdf_f.plot()
plt.show()

first_feature_properties = radd_gdf_f.iloc[1].to_dict()
first_feature_properties


## Check overlap ##
check_overlap = gpd.sjoin(farms_gdf, radd_gdf_f, how="inner", op='intersects')
# It returns an empty dataframe, hence here there is also no overlap

print(check_overlap)
# Again an empty dataframe -- which seems a little strange


## Combine both ## 
gdf_combined = gpd.GeoDataFrame(pd.concat([farms_gdf, radd_gdf_f], ignore_index=True))
gdf_combined['source'] = ['farms_gdf']*len(farms_gdf) + ['radd_gdf_f']*len(radd_gdf_f)
gdf_combined.tail()

# Basic plot
gdf_combined.plot(column='source', legend=True)
plt.show()

# More sophisticated one
color_map = {
    'farms_gdf': 'black',  #magenta
    'radd_gdf_f': 'red'      #cyan
}

# Assign colors based on 'source' using the color map
gdf_combined['color'] = gdf_combined['source'].apply(lambda x: color_map[x])

# Plot again -- with more extended y limits
fig, ax = plt.subplots(figsize=(8,12))
# Plot each group separately to control colors and create labels
for source, color in color_map.items():
    # Select data for each source
    data = gdf_combined[gdf_combined['source'] == source]
    data.plot(ax=ax, color=color, label=source)

# Identify limits
#minx, miny, maxx, maxy = geojson_gdf.total_bounds
# minx = geojson_gdf.total_bounds[0]
# maxx = geojson_gdf.total_bounds[2]
minx = -76
maxx = -75
miny = 1
maxy = 2
# with -78, -75, 0, 2 add the legend at the upper left
# with -76, -75, 1, 2 add the legend at the upper right

# Set the limits of the plot to the bounding box of farms'
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

# Maintain equal aspect ratio to avoid distortion
ax.set_aspect('equal', adjustable='box')

# Custom legend
legend_handles = [mpatches.Patch(color=color, label=label) for label, color in color_map.items()]
ax.legend(handles=legend_handles, title='Source', loc = 'upper right')

plt.show()


# Without combining the geodataframes
fig, ax = plt.subplots(figsize=(8, 12))  # Create a plot figure and axis
farms_gdf.plot(ax=ax, color='blue', edgecolor='k', alpha=0.5)  # Plot the first GeoDataFrame
radd_gdf_f.plot(ax=ax, color='red', edgecolor='k', alpha=0.5)  # Plot the second GeoDataFrame

minx = -76
maxx = -75
miny = 1
maxy = 2
# with -78, -75, 0, 2 add the legend at the upper left
# with -76, -75, 1, 2 add the legend at the upper right

# Set the limits of the plot to the bounding box of farms'
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

ax.set_title('Comparison of Two GeoDataFrames')
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')

plt.show()


# Plotly method
import plotly.graph_objects as go

# Create a Plotly figure
fig = go.Figure()

# Plot each GeoDataFrame
for geom in farms_gdf.geometry:
    x, y = geom.exterior.coords.xy
    fig.add_trace(go.Scatter(x=x, y=y, fill="toself", name='Famrs'))

for geom in radd_gdf_f.geometry:
    x, y = geom.exterior.coords.xy
    fig.add_trace(go.Scatter(x=x, y=y, fill="toself", name='RADD', line=dict(color='red')))

fig.update_layout(title='Comparison', xaxis_title='Longitude', yaxis_title='Latitude')
fig.show()



# 00N_070W
import rasterio
from rasterio.windows import Window

# with rasterio.open('data\\download\\00N_070W.tif') as src:
#         for ji, window in src.block_windows(1):
#             data = src.read(1, window=window)
#             # Process your data here (e.g., analyze, display, store results)
#             print(data)

# Trying to understand the data


# Path to your GeoTIFF file
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


## Load the geotiff info into a geopandas
with rasterio.open(file_path) as src:
    # Get the width and height of the raster dataset
    width = src.width
    height = src.height

    # Get the block sizes (tile sizes)
    block_width, block_height = src.block_shapes[0]  # Assuming all bands have the same block shape

    # Calculate the number of tiles in each dimension
    num_tiles_x = (width + block_width - 1) // block_width
    num_tiles_y = (height + block_height - 1) // block_height

    # Create a list to store tile geometries and associated metadata
    tile_data = []

    # Iterate over each tile
    for i in range(num_tiles_y):
        for j in range(num_tiles_x):
            # Calculate tile bounding box coordinates
            minx = src.bounds.left + j * block_width * src.transform.a
            miny = src.bounds.top - (i + 1) * block_height * src.transform.e
            maxx = minx + block_width * src.transform.a
            maxy = miny + block_height * src.transform.e

            # Create a Polygon geometry representing the tile
            tile_geometry = box(minx, miny, maxx, maxy)

            # Store tile metadata (e.g., tile index, number of tiles in X and Y directions)
            tile_metadata = {
                'tile_index_x': j,
                'tile_index_y': i,
                'num_tiles_x': num_tiles_x,
                'num_tiles_y': num_tiles_y
            }

            # Append tile geometry and metadata to the list
            tile_data.append({'geometry': tile_geometry, **tile_metadata})

# Create a GeoDataFrame from the list of tile geometries and metadata
tiles_gdf = gpd.GeoDataFrame(tile_data)

# Print the GeoDataFrame
print(tiles_gdf)

## Takes too long, alternative
from rasterio.windows import Window
import numpy as np
from shapely.geometry import Point


# Simplify the processing loop and increase chunk size for efficiency
chunk_size = 10000  # Larger chunk size to reduce number of iterations

from rasterio.features import shapes

# Function to process each chunk of the raster
def process_chunk(dataset, window):
    # Read the raster data for the given window
    image = dataset.read(1, window=window)
    
    # Create a mask with non-zero values
    mask = image != 0
    
    # Extract shapes from the mask
    results = shapes(image, mask=mask, transform=rasterio.windows.transform(window, dataset.transform))
    
    # Create polygons from the shapes
    geometries = [shape(geom) for geom, value in results if value == 1]
    return geometries



# Open the GeoTIFF file
#with rasterio.open(file_path) as src:
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
        # Create a mask with non-zero values
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
        # chunk_geometries = process_chunk(src, window)
        # Append the results
        all_geometries.extend(chunk_geometries)

# Create a GeoDataFrame
if all_geometries:
    gdf = gpd.GeoDataFrame({'geometry': all_geometries}, crs=src.crs)
else:
    print("No geometries were created from the raster data.")

gdf.plot()
plt.show()

# Save the GeoDataFrame to a file (e.g., Shapefile)
output_path = 'data/download/output/00N_080W.shp'
# gdf.to_file(output_path)
# with open(output_path, 'w') as f:
#     f.write(gdf.to_json())
# Chunked writing
# Define the output file path
output_file = 'data/download/output/00N_080W.gpkg'

# Save the GeoDataFrame to Geopackage with chunking
# chunk_size = 10000 
# with gpd.GeoDataFrame() as chunked_gdf:
#     for i in range(0, len(gdf), chunk_size):
#         chunk = gdf.iloc[i:i+chunk_size]
#         chunk.to_file(output_file, driver='GPKG', append=i!=0)


import geopandas as gpd
import os

# Load your GeoDataFrame
# geo_df = ...

# Define the output directory and base file name
output_dir = 'data/download/output/00N_080W_output_chunks'
base_filename = 'output_chunk_'

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Define the chunk size
# chunk_size = 10000  # Adjust as needed

# Save the GeoDataFrame to Geopackage in chunks
for i, chunk_start in enumerate(range(0, len(gdf), chunk_size)):
    chunk_end = min(chunk_start + chunk_size, len(gdf))
    chunk = gdf.iloc[chunk_start:chunk_end]
    output_file = os.path.join(output_dir, f"{base_filename}{i}.gpkg")
    chunk.to_file(output_file, driver='GPKG')

input_file = 'data/download/output/00N_080W_output_chunks/output_chunk_3.gpkg'
with fiona.open(input_file, 'r', driver='GPKG') as src:
    # Get the schema of the input file
    schema = src.schema
    schema

# Merge the chunked Geopackage files into a single file
# os.system(f"ogrmerge.py -o {output_file} {output_dir}/*.gpkg")


import subprocess

# Merge the chunked Geopackage files into a single file using subprocess
output_file = 'data/download/output/00N_080W_merged_output.gpkg'
# subprocess.run(['ogrmerge.py', '-o', output_file, 'output_chunks/*.gpkg'], shell=True)

import fiona

# List of paths to individual Geopackage files
input_files = ['data/download/output/00N_080W_output_chunks/output_chunk_0.gpkg', 'data/download/output/00N_080W_output_chunks/output_chunk_1.gpkg', 'data/download/output/00N_080W_output_chunks/output_chunk_3.gpkg', 'data/download/output/00N_080W_output_chunks/output_chunk_4.gpkg']

# Output file path for the merged Geopackage file
# output_file = 'merged_output.gpkg'

# Define schema for the output file
schema = {'geometry': 'Polygon', 'properties': {}}

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

# print("Merging complete.")

merged_output = gpd.read_file(output_file)
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










