# Debugging style_function
import folium
import streamlit as st
import geopandas as gpd
import streamlit.components.v1 as components

# Load your GeoPandas dataframe
gdf = gpd.read_file('data\\input\\processed\\radd_gdf.geojson')  # or .geojson or any other supported format

# # Check the first few rows of the dataframe to ensure it's loaded correctly
# st.write(gdf.head())

# # Check the CRS of the dataframe and convert to WGS84 if necessary
# if gdf.crs != "EPSG:4326":
#     gdf = gdf.to_crs("EPSG:4326")

# # Display CRS for debugging
# st.write("CRS:", gdf.crs)

# # Create Folium map centered around the data
latitude = gdf.geometry.centroid.y.mean()
longitude = gdf.geometry.centroid.x.mean()
m = folium.Map(location=[latitude, longitude], zoom_start=10)

# # Simple style function with a static color
# def simple_style_function(feature):
#     return {
#         'fillColor': '#FFBF00',  # Static fill color
#         'color': '#000000',      # Border color
#         'weight': 1,             # Border weight
#         'fillOpacity': 0.6       # Fill opacity
#     }

# # Add GeoJSON layer to the map with the simple style function
# folium.GeoJson(
#     gdf,  # Pass GeoDataFrame directly
#     style_function=simple_style_function  # Apply the simple style function to each feature
# ).add_to(m)

# # Display Folium map in Streamlit
# components.html(m._repr_html_(), width=700, height=500)

# Next step
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

# Check the first few rows of the dataframe to ensure it's loaded correctly
st.write(gdf.head())

# Check the CRS of the dataframe and convert to WGS84 if necessary
if gdf.crs != "EPSG:4326":
    gdf = gdf.to_crs("EPSG:4326")

# Display CRS for debugging
st.write("CRS:", gdf.crs)

# Define a list of unique text values in the 'value' column
unique_values = gdf['conf_level'].unique()

# Create a colormap for these unique values
if len(unique_values) == 2:
    colors = ['#1f77b4', '#ff7f0e']  # Example: blue and orange
else:
    cmap = plt.cm.get_cmap('coolwarm', len(unique_values))
    colors = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]

# Map text values to colors, converting keys to strings to avoid serialization issues
value_to_color = {str(k): v for k, v in zip(unique_values, colors)}

# Print the color mapping for debugging
st.write("Color mapping:", value_to_color)

# Enhanced style function with colormap logic
def style_function(feature):
    value = str(feature['properties']['conf_level'])  # Convert value to string to match keys
    color = value_to_color.get(value, '#FFFFFF')  # Get the corresponding color or default to white
    # Print each feature's style for debugging
    #st.write("Feature value:", value, "Color:", color)
    return {
        'fillColor': color,  # Set fill color
        'color': color,  # Border color (use same color to debug)
        'weight': 0,         # Border weight (set to 1 for debugging)
        'fillOpacity': 0.6   # Set fill opacity
    }

# Add GeoJSON layer to the map with the enhanced style function
folium.GeoJson(
    gdf,  # Pass GeoDataFrame directly
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['conf_level'])  # Apply the enhanced style function to each feature
).add_to(m)


# Display Folium map in Streamlit
components.html(m._repr_html_(), width=700, height=500)

