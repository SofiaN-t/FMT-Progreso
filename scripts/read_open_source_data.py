## Libraries ##
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show


## Read files ##
# Coffee plots -- to identify the crs
# path
plots_path = "data\\input\\processed\\plots_colombia.geojson"
# file
plots_gdf = gpd.read_file(plots_path)
# Optional
# plots_gdf.info()
# plots_gdf.crs
# Keep the epsg based on observations on the other file
# geojson_gdf_epsg = plots_gdf.crs.to_epsg()
# Check amount of data
# plots_gdf.shape[0] #42


# Amazonian Colombia
# path
amaz_path = "data\\input\\raw\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp"
# file
# geopandas as the best library for shapefile -- no windows function available
amaz_gdf = gpd.read_file(amaz_path) # it will take a while
# Optional
# amaz_gdf.info()
# amaz_gdf.head() # will take some time
# amaz_gdf.geom_type.unique()
# amaz_gdf.crs
### Observations: ###
# For the shapefile to be read, you also need all of the rest required files 
# When printing the head, last col indicates multipolygons io polygons -- will have to be treated
# deforestac column includes other events, not only lost forest -- will have to be filtered
# geometry = 'polygons'
# coordinate system is different than the one for the coffee plots  file

# Transform file #
# From multipolygons to polygons
amaz_gdf = amaz_gdf.explode(index_parts=True)

# Filtering for only deforestation areas
amaz_gdf = amaz_gdf.loc[amaz_gdf['deforestac'] == 'Perdida']

# Transform the crs based on farms' crs
amaz_gdf = amaz_gdf.to_crs(plots_gdf.crs.to_epsg())
# amaz_gdf.shape[0] # 13154
# amaz_gdf.crs
# Succesfully transformed from multipolygon to polygons
# Succesfully filtered for lost forest
# Successfully transformed crs


# RADD alerts over specific tile
radd_path = 'data/input/raw/10N_080W.tif'
lat_range = [1.8, 2]  # y-axis
lon_range = [-76.5, -75.5]  # x-axis
only_alerts = False # used to select what to visualise

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

    # Read the data within the window
    image = src.read(window=window)

    # Get the transformation for the window
    transform = src.window_transform(window)

    # Convert window bounds to geographic coordinates
    bounds = src.window_bounds(window)

# Apply a mask to the data (if triggered) to only identify the alerts
if only_alerts == True:
    masked_image = np.where(image > 0, image, np.nan)  # Replace negative values with np.nan
else:
    masked_image = image

fig, ax = plt.subplots(figsize=(10, 10))
ax.set_facecolor('white') #backgr
vmin, vmax = masked_image.min(), masked_image.max()
show(masked_image, transform=transform, ax=ax, cmap='viridis', vmin=vmin, vmax=vmax, alpha=0.5, extent=bounds)
plt.show()
