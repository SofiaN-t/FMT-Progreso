## Libraries ##
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.patches as mpatches

## Read files ##
# geojson
# path
geojsonfile_path = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
# file
geojson_gdf = gpd.read_file(geojsonfile_path)
geojson_gdf.info()
geojson_gdf.crs
# Keep the epsg based on observations on the other file
geojson_gdf_epsg = geojson_gdf.crs.to_epsg()
# Check shape
geojson_gdf.shape[0] #42

# shapefile
# path
shapefile_path = "C:\\Users\\user\\Documents\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp"
# file
shapefile_gdf = gpd.read_file(shapefile_path)
shapefile_gdf.info()
shapefile_gdf.head()
shapefile_gdf.geom_type.unique()
shapefile_gdf.crs
# shapefile_gdf.describe()
### Observations: ###
# For the shapefile to be read, you also need all of the rest required files 
# When printing the head, last col indicates multipolygons io polygons -- will have to be treated
# deforestac column includes other events, not only lost forest -- will have to be filtered
# geometry = 'polygons'
# coordinate system is different than the one for the geojson file

## Transform files ##
# From multipolygons to polygons
shapefile_gdf = shapefile_gdf.explode()

# Filtering for only deforestation areas
shapefile_gdf = shapefile_gdf.loc[shapefile_gdf['deforestac'] == 'Perdida']

# Transform the crs based on farms' crs
shapefile_gdf = shapefile_gdf.to_crs(geojson_gdf_epsg)

shapefile_gdf.head()
shapefile_gdf['deforestac'].unique()
shapefile_gdf.shape[0] # 13154
shapefile_gdf.crs
# Succesfully transformed from multipolygon to polygons
# Succesfully filtered for lost forest
# Successfully transformed crs

## Plot files ##
# Plot the shapefile
fig, ax = plt.subplots()
# minx=shapefile_gdf.total_bounds[0]
# maxx=-71
# miny=-2
# maxy=0#shapefile_gdf.total_bounds[3]
shapefile_gdf.plot(ax=ax)
# ax.set_xlim(minx, maxx)
# ax.set_ylim(miny, maxy)
plt.show()

# Plot the geojson file
# Plot the shapefile
geojson_gdf.plot()
plt.show()

## Check overlap ##
# Function to check overlap
# Assuming you want to check if any polygon in the GeoJSON overlaps with any polygon in the shapefile
# Loop through each geometry in one GeoDataFrame and check against all in the other
count=0
for index, geojson_geom in geojson_gdf.iterrows():
    for _, shapefile_geom in shapefile_gdf.iterrows():
        count = count + 1
        if geojson_geom.geometry.intersects(shapefile_geom.geometry):
            print(f"Overlap found between polygons at GeoJSON index {index} and shapefile.")
        # else:
        #     print("No overlap")
print(count)
## Observations: ##
# There does not seem to be some overlap 
# There are 552468 (42*13154) combinations checked

# Alternatively, less computationally expensive
check_overlap = gpd.sjoin(geojson_gdf, shapefile_gdf, how="inner", op='intersects')
# It returns an empty dataframe, hence here there is also no overlap

print(check_overlap) # empty dataframe

## Combine two geodataframes ##
gdf_combined = gpd.GeoDataFrame(pd.concat([geojson_gdf, shapefile_gdf], ignore_index=True))
gdf_combined.head()
gdf_combined.tail()

## Check overlap when there is one ##
bench_overlap = gpd.sjoin(geojson_gdf, gdf_combined, how="inner", op='intersects')
bench_overlap.head()

### Observations ###
# Here, bench_overlap shows the plots that are the same with a left and right identification of the same columns

## Plot geodataframes on the same map ##
# Add source column to differentiate dataframes
gdf_combined['source'] = ['geojson_gdf']*len(geojson_gdf) + ['shapefile_gdf']*len(shapefile_gdf)
gdf_combined['source'].tail()

# Plot in one
gdf_combined.plot(column='source', legend=True)
plt.show()
### Observations ###
# The different polygons are not visible 
# We will have to use more contrasting colors

# Refine plot
# Make a color map to assign specific colors
color_map = {
    'geojson_gdf': 'black',  #magenta
    'shapefile_gdf': 'red'      #cyan
}

# Assign colors based on 'source' using the color map
gdf_combined['color'] = gdf_combined['source'].apply(lambda x: color_map[x])

# Plot again -- with custom-made colors
fig, ax = plt.subplots()
for label, group in gdf_combined.groupby('source'):
    group.plot(ax=ax, color=group['color'].iloc[0], label=label)
# gdf_combined.plot(ax=ax, color=[color_map[source] for source in gdf_combined['source']], legend=True)
ax.legend(title='Source')
# Not easy to add a legend when you've custom made the colors
ax.set_facecolor('lightgrey') # optional -- it doesn't seem to add a lot
plt.show()

### Observations ###
# Other than the plot limits (which will be addressed later), 
# we notice that the legend is not visible
# It is not easy to plot the legend when you've custom-made the colors so, next attempt:

# Plot again -- with legend
fig, ax = plt.subplots()

# Plot each group separately to control colors and create labels
for source, color in color_map.items():
    # Select data for each source
    data = gdf_combined[gdf_combined['source'] == source]
    data.plot(ax=ax, color=color, label=source)

# Creating custom legend handles
legend_handles = [mpatches.Patch(color=color, label=label) for label, color in color_map.items()]
ax.legend(handles=legend_handles, title='Source')
plt.show()

# Let's zoom in the area of the farms' polygons
# Same plot with set limits based on geojson
fig, ax = plt.subplots()
# Plot each group separately to control colors and create labels
for source, color in color_map.items():
    # Select data for each source
    data = gdf_combined[gdf_combined['source'] == source]
    data.plot(ax=ax, color=color, label=source)

# Identify limits
minx, miny, maxx, maxy = geojson_gdf.total_bounds

# Set the limits of the plot to the bounding box of farms'
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

legend_handles = [mpatches.Patch(color=color, label=label) for label, color in color_map.items()]
ax.legend(handles=legend_handles, title='Source')
plt.show()

### Observations ###
# When zooming in so much, we do not see the shapefile polygons
# We will extend the limits to include wider range of (at least) y values

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

# LEgend out of plot area
# Shrink current axis's height by 10% on the bottom
# box = ax.get_position()
# ax.set_position([box.x0, box.y0 + box.height * 0.1,
#                  box.width, box.height * 0.9])

# # Put a legend below current axis
# ax.legend(handles = legend_handles, title='Source', loc='upper center', bbox_to_anchor=(0.5, -0.05),
#           fancybox=True, shadow=True)
# Is not very visible anymore
plt.show()

### Observations ###
# The areas do not overlap at any point and cutting to the limits does not particularly help get
# a glimpse for both
# However, looking closely you should be able to see both
# The idea is to split in 4

# Plot again -- in different subplots

# Identify the limits
minx, miny, maxx, maxy = gdf_combined.total_bounds
# Calculate the midpoints
mid_x, mid_y = (minx + maxx) / 2, (miny + maxy) / 2
# Create a figure with 4 subplots (2x2)
fig, axs = plt.subplots(2, 2, figsize=(10, 15))  # Adjust figsize as needed
# Define the bounds for each quadrant
quadrants = {
    (0, 0): (minx, mid_x, mid_y, maxy),  # Top-left
    (0, 1): (mid_x, maxx, mid_y, maxy),  # Top-right
    (1, 0): (minx, mid_x, miny, mid_y),  # Bottom-left
    (1, 1): (mid_x, maxx, miny, mid_y),  # Bottom-right
}

# Plot each quadrant in its respective subplot
for (row, col), (minx_, maxx_, miny_, maxy_) in quadrants.items():
    ax = axs[row, col]
    #gdf_combined.plot(ax=ax)
    for source, color in color_map.items():
        data = gdf_combined[gdf_combined['source'] == source]
        data.plot(ax=ax, color=color)

    # Set the limits for each subplot to focus on the quadrant
    ax.set_xlim(minx_, maxx_)
    ax.set_ylim(miny_, maxy_)
    ax.set_aspect('equal', adjustable = 'box')

    # Customize each subplot if needed
    # ax.set_title(f"Quadrant {row+1}, {col+1}")
    # ax.set_xlabel('Longitude')
    # ax.set_ylabel('Latitude')

    # xtick parameters
    ax.tick_params(axis='x', which='both', bottom=True, top=False, labelbottom=True)

# Legend
legend_handles = [mpatches.Patch(color=color, label=label) for label, color in color_map.items()]
ax.legend(handles=legend_handles, title='Source', loc = 'upper left')

# Adjust layout
plt.tight_layout()
plt.show()

### Observations ###
# Subplots do not help 









## Deprecated ##
                    # # Alternative (?) way of plotting
                    # # Without having to combine the geodataframes
                    # # shapefile_gdf = shapefile_gdf.to_crs(geojson_gdf.crs)

                    # fig, ax = plt.subplots(figsize=(15, 15))
                    # shapefile_gdf.plot(ax=ax, alpha=0.4, color="red")
                    # geojson_gdf.plot(ax=ax, alpha=1, color="black")
                    # plt.show()
                    # # Not sure how to add a legend like that