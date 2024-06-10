## Libraries ##
import sys
import os
import pandas as pd
import geopandas as gpd
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.plot import show
from rasterio.windows import from_bounds
from shapely.geometry import mapping, Polygon
import geojson

## Functions ##
# Extract year from radd values
def extract_year(value):
    if value == 0:
        return None
    days_since = int(str(value)[1:])
    start_date = pd.Timestamp('2014-12-31')
    alert_date = start_date + pd.Timedelta(days=days_since)
    return alert_date.year

def extract_confidence_level(value):
    if value == 0:
        return None
    conf_value = int(str(value)[0])
    if conf_value == 2:
        conf_level = 'low'
    elif conf_value == 3:
        conf_level = 'high'
    else:
        conf_level = 'n/a'
    return conf_level


# Check if running in an interactive environment eg when running line-by-line
def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

# Add the root directory to the sys.path if not running interactively
if not is_interactive():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load configuration file
from utils import load_config
config = load_config()


## Read files ##
# Coffee plots -- to identify the crs
# path
plots_path = os.path.abspath(config['data_paths']['processed']['coffee_plots'])
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
amaz_path = os.path.abspath(config['data_paths']['raw']['amazon'])
# file
# geopandas as the best library for shapefile -- no windows function available
amaz_shp_raw = gpd.read_file(amaz_path) # it will take a while
# Optional
# amaz_shp.info()
# amaz_shp.head() # will take some time
# amaz_shp.geom_type.unique()
# amaz_shp.crs

### Observations: ###
# For the shapefile to be read, you also need all of the rest required files 
# Columns that show areas are collective, do not show the particular polygon -- probably drop
# When printing the head, last col indicates multipolygons io polygons -- will have to be treated
# A multiindex dataframe -- related to deforestac column? -- will have to be checked and treated
# deforestac column includes other events, not only lost forest -- will have to be filtered
# geometry = 'polygons'
# coordinate system is different than the one for the coffee plots  file

# Transform file #
# From multipolygons to polygons
amaz_shp_expl = amaz_shp_raw.explode(index_parts=True)

# Check again the multiindex
# amaz_shp.head()
# It looks like it is related with the different categories -- Will treat it at next step

# Filtering for only deforestation areas
amaz_shp = amaz_shp_expl.loc[amaz_shp_expl['deforestac'] == 'Perdida']

# Remove multi-index 
amaz_shp = amaz_shp.reset_index() # level_0, level_1, ...
# Drop unnecessary columns
amaz_shp = amaz_shp.drop(columns=['level_0', 'area_ha', 'st_area_sh', 'st_perimet'])

# Transform the crs based on farms' crs
if amaz_shp.crs != plots_gdf.crs:
    amaz_shp = amaz_shp.to_crs(plots_gdf.crs.to_epsg())

## Observations ##
# amaz_shp_expl.shape[0] #29075
# amaz_shp.shape[0] # 13154
# amaz_shp.crs
# Succesfully transformed from multipolygon to polygons
# Succesfully filtered for lost forest
# Succesfully dropped unnecessary columns
# Successfully transformed crs

# Save in geopandas dataframe
amaz_geojson_path = config['data_paths']['processed']['amazon']
amaz_shp.to_file(amaz_geojson_path, driver='GeoJSON')
# # Check the writing
# amaz_gdf=gpd.read_file(amaz_geojson_path)
# amaz_gdf.head()

# RADD alerts over specific tile
radd_path = os.path.abspath(config['data_paths']['raw']['radd'])

# Define the bounding box (longitude and latitude)
min_lon, min_lat = -76.5, 1.8
max_lon, max_lat = -75.5, 2
# This can also be customized as desired
# To define the limits based on the coffee farms, you can use
# min_lon, min_lat = plots_gdf.total_bounds[0], plots_gdf.total_bounds[1]
# max_lon, max_lat = plots_gdf.total_bounds[2], plots_gdf.total_bounds[3]

with rasterio.open(radd_path) as src:
    # Transform bounding box coordinates to the coordinate reference system of the .tif
    bounds = [min_lon, min_lat, max_lon, max_lat]
    window = from_bounds(*bounds, transform=src.transform)
    
    # Read the window (only part) of data
    data = src.read(1, window=window)
    
    # Get the affine transform for the window
    # To go from raster to geographical coordinates
    transform = src.window_transform(window)

# Create a list of polygons with their values
features = []
for j in range(data.shape[0]):
    for i in range(data.shape[1]):
        value = data[j, i]
        if value > 0:  # Retain only positive values which are those that show an alert
            x, y = transform * (i, j) # Use the transformation to go to 'normal' (x,y) coordinates
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

# Save the transformed to a geojson file
radd_geojson_path = config['data_paths']['processed']['radd']
with open(radd_geojson_path, 'w') as f:
    geojson.dump(feature_collection, f)

# Enhance #
# Read in as geopandas
radd_gdf=gpd.read_file(radd_geojson_path)
# Add the necessary columns to transform value to year and confidence level
# Apply the function to extract year
radd_gdf['year'] = radd_gdf['value'].apply(extract_year)
# Applying the function to add confidence level
radd_gdf['conf_level'] = radd_gdf['value'].apply(extract_confidence_level)
# Save to geopandas
if radd_gdf.crs != plots_gdf.crs:
    radd_gdf = radd_gdf.to_crs(plots_gdf.crs.to_epsg())
    
radd_gdf.to_file(radd_geojson_path, driver='GeoJSON')