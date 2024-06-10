## Libraries ##
import sys
import os
import pandas as pd
# If it throws an error, install the package that is missing
import json
import geopandas as gpd


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


## Choices ## 
# To distinguish between potentially different formats
provided_file_type = 'xlsx'
geojson_col_exists = 'yes'


## Steps to go from xlsx to geojson ##
if (provided_file_type == 'xlsx') & (geojson_col_exists == 'yes'):
    # Read the provided excel file
    col_excel_path = config['data_paths']['raw']['coffee_plots']
    col_excel_raw = pd.read_excel(col_excel_path)
    # Show the provided excel file
    col_excel_raw.head()
### Observations: ###
# We see that the file is constructed in a way that is easy to extract the geojson related information
# via column 'Coffee plot Geojson (1)'

# We also see that there is an individual plot_is column and an element in the geojson column that is called plot_id
# that do NOT coincide TODO


## To get the geojson information ##
# As mentioned, we will focus on one column with the geopspatial info
# When the provided file is not in the same format, the manipulation might need to be changed.
geojson_col = 'Coffee plot GeoJson (1)'

# Filter out rows where the GeoJSON data is not present or is not a valid JSON string in the excel file
valid_geojson_data = col_excel_raw[col_excel_raw[geojson_col].str.startswith('{', na=False)][geojson_col]

# Load each GeoJSON string, skipping any that cause a JSONDecodeError
features = []
for geojson_str in valid_geojson_data:
    try:
        geojson_obj = json.loads(geojson_str)
        features.append(geojson_obj)
    except json.JSONDecodeError:
        # Skip any GeoJSON strings that are not correctly formatted
        continue

# Compile these into a single GeoJSON FeatureCollection.
# You would need that in the case that your geojson column is already flattened 
# and "features" include type="Feature" and NOT type="FeatureCollection"

flattened_features = []
for feature in features:
    # Check if the feature is a FeatureCollection
    if feature['type'] == 'FeatureCollection':
        # If so, extend the flattened_features list with its features
        flattened_features.extend(feature['features'])
    else:
        # If it's a single Feature, just append it to the list
        flattened_features.append(feature)

# Create a new GeoJSON FeatureCollection with the flattened structure
flat_geojson = {
    "type": "FeatureCollection",
    "features": flattened_features
}

# Save the flattened GeoJSON to a new file
flat_geojson_file_path = config['data_paths']['processed']['coffee_plots']
with open(flat_geojson_file_path, 'w') as file:
    json.dump(flat_geojson, file)


## Read the produced geojson to check ##
# sample=gpd.read_file("data\\input\\processed\\plots_colombia.geojson")
# sample.head()


