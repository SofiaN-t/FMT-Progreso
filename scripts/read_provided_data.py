## First attempt to read the provided geojson file
# https://stackoverflow.com/questions/19098667/order-of-coordinates-in-geojson
# -- install it first with 'pip install geopandas'
import geopandas as gpd
sample=gpd.read_file("data\\raw\\polygon1.geojson")
print(sample.head())
### Can't infer much at this point


## To read a geojson and check whether two polygons overlay
# ChatGPT
import json
from shapely.geometry import shape, Polygon

# Read the GeoJSON file
with open("data\\raw\\polygon1.geojson") as f:
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
gdf = gpd.read_file('data\\raw\\Export_TEST.csv')

# convert the GeoDataFrame to a geojson object
geo_json = gdf.to_json()
print(geo_json)

# however if the objects become very big, store the GeoDataFrame to a .geojson file
gdf.to_file('path', driver='GeoJSON')
### There are a number of irrelevant columns that cannot be converted with this method

## Alternative
# GPT
import csv
# install first
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
csv_filename = 'data\\raw\\Export_TEST.csv'
geojson_filename = 'data\\raw\\output\\output.geojson'

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


