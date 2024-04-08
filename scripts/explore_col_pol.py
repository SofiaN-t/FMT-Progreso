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

# Rename columns to eliminate spaces TODO

# Save as csv
# col_excel_raw.to_csv("data\\raw\\Polygons_EAE_project_Progreso.csv")
# no need for that, can go directly to geojson from excel


## To get the geojson information ##
# As mentioned, we will focus on one column with the geopspatial info

# Filter out rows where the GeoJSON data is not present or is not a valid JSON string in the excel file
valid_geojson_data_ods = col_excel_raw[col_excel_raw['Coffee plot GeoJson (1)'].str.startswith('{', na=False)]['Coffee plot GeoJson (1)']

# Load each GeoJSON string, skipping any that cause a JSONDecodeError
features_ods = []
for geojson_str in valid_geojson_data_ods:
    try:
        geojson_obj = json.loads(geojson_str)
        features_ods.append(geojson_obj)
    except json.JSONDecodeError:
        # Skip any GeoJSON strings that are not correctly formatted
        continue


# Compile these into a single GeoJSON FeatureCollection.
features_ods = [json.loads(geojson_str) for geojson_str in valid_geojson_data_ods]


flattened_features = []
for feature in features_ods:
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
flat_geojson_file_path = 'data\\raw\\output\\Polygons_EAE_project_Progreso_xlsx_flattened.geojson'
with open(flat_geojson_file_path, 'w') as file:
    json.dump(flat_geojson, file)

flat_geojson_file_path




# Create a GeoJSON FeatureCollection for the ODS data
geojson_ods = {
    "type": "FeatureCollection",
    "features": features_ods
}

# Save the GeoJSON to a file
geojson_file_path_ods = 'data\\raw\\output\\Polygons_EAE_project_Progreso_csv.geojson'
with open(geojson_file_path_ods, 'w') as file:
    json.dump(geojson_ods, file)

geojson_file_path_ods



## Read the produced geojson ##
import geopandas as gpd
sample=gpd.read_file("data\\raw\\output\\Polygons_EAE_project_Progreso_xlsx_flattened.geojson")
print(sample.head())
# Weird structure



# Flatten the GeoJSON structure by extracting features from nested FeatureCollections
flattened_features = []
for feature in features_ods_corrected:
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
flat_geojson_file_path = '/mnt/data/flat_exported_geojson_ods.geojson'
with open(flat_geojson_file_path, 'w') as file:
    json.dump(flat_geojson, file)

flat_geojson_file_path


