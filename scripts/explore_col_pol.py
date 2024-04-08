## Libraries ##
import pandas as pd
# If it throws an error, install the package that is missing
import json
import geopandas


## Functions ##
# to be seen whether is better to wrap code in function


## Steps to go from xlsx to geojson ##
# Read the provided excel file
col_excel_raw = pd.read_excel("data\\raw\\Polygons_EAE_project_Progreso.xlsx")
# Show the provided excel file
col_excel_raw.head()
### Observations: ###
# We see that the file is constructed in a way that is easy to extract the geojson related information
# via column 'Coffee plot Geojson (1)'

# We also see that there is an individual plot_is column and an element in the geojson column that is called plot_id
# that do NOT coincide TODO

# Rename columns to eliminate spaces TODO

# Save as csv
# col_excel_raw.to_csv("data\\raw\\Polygons_EAE_project_Progreso.csv")
# no need for that, can go directly to geojson from excel


## To get the geojson information ##
# As mentioned, we will focus on one column with the geopspatial info
geojson_col = 'Coffee plot GeoJson (1)'

# Filter out rows where the GeoJSON data is not present or is not a valid JSON string in the excel file
valid_geojson_data = col_excel_raw[col_excel_raw[geojson_col].str.startswith('{', na=False)][geojson_col]

# Load each GeoJSON string, skipping any that cause a JSONDecodeError
features = [] # features_ods
for geojson_str in valid_geojson_data:
    try:
        geojson_obj = json.loads(geojson_str)
        features.append(geojson_obj)
    except json.JSONDecodeError:
        # Skip any GeoJSON strings that are not correctly formatted
        continue

# Compile these into a single GeoJSON FeatureCollection.
# features_ods = [json.loads(geojson_str) for geojson_str in valid_geojson_data_ods]
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
flat_geojson_file_path = 'data\\raw\\output\\Polygons_EAE_project_Progreso.geojson'
with open(flat_geojson_file_path, 'w') as file:
    json.dump(flat_geojson, file)

flat_geojson_file_path


## Read the produced geojson to check ##
import geopandas as gpd
sample=gpd.read_file("data\\raw\\output\\Polygons_EAE_project_Progreso.geojson")
sample.head()


