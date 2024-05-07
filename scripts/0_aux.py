## Read a file 
import fiona
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


## Save the geodataframe to a file 
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


## Load the geotiff info into a geopandas ##
file_path = 'data\\download\\00N_080W.tif'
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
## Takes too long

## To read in batches (windows) ##
import rasterio
from rasterio.windows import Window

# with rasterio.open('data\\download\\00N_070W.tif') as src:
#         for ji, window in src.block_windows(1):
#             data = src.read(1, window=window)
#             # Process your data here (e.g., analyze, display, store results)
#             print(data)


## To check explore ##
import geopandas as gpd
import geodatasets
import matplotlib.pyplot as plt

df = gpd.read_file(geodatasets.get_path("geoda.chicago_health"))
df.head()
df.columns
explore_df=df.explore("community", cmap="Blues")
output_file = "example_community.html"
explore_df.save(output_file)

import webbrowser
webbrowser.open(output_file, new=2)


## To keep some plotting methods ## 
# Files
farms_filepath = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
farms_gdf = gpd.read_file(farms_filepath)

radd_filepath = "data/download/RADD.geojson"
radd_gdf = gpd.read_file(radd_filepath)

# Plot without combining the geodataframes
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
