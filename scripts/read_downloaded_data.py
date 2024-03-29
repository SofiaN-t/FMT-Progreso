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

# Open the raster file
with rasterio.open("data\\peru_decrease_2004_01_01_to_2023_01_01.asc") as src:
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
