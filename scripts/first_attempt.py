## First attempt to read the geojson file
# https://stackoverflow.com/questions/19098667/order-of-coordinates-in-geojson
# import geopandas as gpd
# sample=gpd.read_file("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\polygon1.geojson")
# print(sample.head())
### Doesn't seem to give me meaningful insights


## To read a geojson and check whether two polygons overlay
# ChatGPT
import json
from shapely.geometry import shape, Polygon

# Read the GeoJSON file
with open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\polygon1.geojson") as f:
    data = json.load(f)

# When converting the csv to geojson
# data = geo_json
### Look below why there needs to be extra treatment
    
# Extract polygons from the GeoJSON
polygons = []
for feature in data['features']:
    polygon_geojson = feature['geometry']
    polygon = shape(polygon_geojson)
    polygons.append(polygon)

# Check for intersection between two polygons
def polygons_overlay(poly1, poly2):
    return poly1.intersects(poly2)

# Example usage
polygon1 = polygons[0]  # Assuming you have two polygons
polygon2 = polygons[1]
overlay = polygons_overlay(polygon1, polygon2)
print("Polygons overlay:", overlay)
### It appears that the geojson file has only one polygon



## To convert a csv to geojson
# https://stackoverflow.com/questions/75298179/convert-pandas-column-with-featurecollection-to-geojson
import geopandas as gpd

# read the CSV file into a GeoDataFrame
gdf = gpd.read_file('C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\Export_TEST.csv')

# convert the GeoDataFrame to a geojson object
geo_json = gdf.to_json()
print(geo_json)

# however if the objects become very big, store the GeoDataFrame to a .geojson file
gdf.to_file('path', driver='GeoJSON')
### There are a number of irrelevant columns that cannot be converted with this method

## Alternative
# GPT
import csv
import geojson

# Function to convert CSV rows to GeoJSON Features
def csv_to_geojson_feature(row):
    properties = {}  # Dictionary to hold properties
    for key, value in row.items():
        # Assuming the column names are keys and values are their corresponding values
        properties[key] = value
    geometry = None  # You need to define the geometry for your features
    feature = geojson.Feature(geometry=geometry, properties=properties)
    return feature

# Read the CSV file
csv_filename = 'C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\Export_TEST.csv'
geojson_filename = 'C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\output.geojson'

features = []

with open(csv_filename, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        feature = csv_to_geojson_feature(row)
        features.append(feature)

# Create a FeatureCollection
feature_collection = geojson.FeatureCollection(features)

# Write the FeatureCollection to a GeoJSON file
with open(geojson_filename, 'w') as f:
    geojson.dump(feature_collection, f)

print(f"GeoJSON file '{geojson_filename}' created successfully.")


## Use a downloaded file from Global Forest Watch
# Read the GeoJSON file
import json
with open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\data\\Deforestation_alerts_(RADD).geojson") as f:
    data = json.load(f)

# Extract polygons from the GeoJSON
from shapely.geometry import shape, Polygon
polygons = []
for feature in data['features']:
    polygon_geojson = feature['geometry']
    polygon = shape(polygon_geojson)
    polygons.append(polygon)

polygons

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
# from PIL import Image

# # Open the .tif file
# image = Image.open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\data\\10N_090W.tif")

# # Display the image
# image.show()
### image decompression bomb error!! could be decompression bomb DOS attack


### Use a .asc file from https://www.arcgis.com/home/item.html?id=ffae4a5b46be4cdd8ce55486fe13df55
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape
import fiona
from fiona.crs import from_epsg

# Open the raster file
with rasterio.open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\data\\peru_decrease_2004_01_01_to_2023_01_01.asc") as src:
    # Read the raster data
    data = src.read(1) # Assuming it's a single-band raster

    # Get the transform and shape of the raster
    transform = src.transform
    width = src.width
    height = src.height

    print(transform)
    print(width)
    print(height)

    # Generate shapes from the raster data
    geom = list(shapes(data, transform=transform))

# Convert the shapes to Shapely geometries
geometries = [shape(geom) for geom, _ in geom]

# Define the output shapefile schema
schema = {
    'geometry': 'Polygon',
    'properties': {'id': 'int'},
}

# Write the geometries to a shapefile
### Have not run this yet
with fiona.open('output.shp', 'w', crs=from_epsg(4326), driver='ESRI Shapefile', schema=schema) as output:
    for i, geometry in enumerate(geometries):
        output.write({
            'geometry': geometry,
            'properties': {'id': i+1},  # Assigning an ID to each feature
        })


## Convert a .tif to a geojson file
import rasterio
from rasterio.features import shapes
import json

# Open the GeoTIFF file
with rasterio.open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\data\\30N_120W.tif") as src:
    # Read the raster data
    data = src.read(1)  # Assuming it's a single-band raster
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
with open("output.geojson", "w") as output_file:
    json.dump(geojson_obj, output_file)


## Explore a .tif file
# Open the GeoTIFF file
with rasterio.open("C:\\Users\\user\\Documents\\EAE\\FMT - Progreso\\data\\30N_120W.tif") as src:
    # Check the data type
    data_type = src.dtypes[0]  # Assuming it's a single-band raster
    # Check the number of bands
    num_bands = src.count
    # Check the coordinate reference system (CRS)
    crs = src.crs
