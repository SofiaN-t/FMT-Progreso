import streamlit as st
import os
import geopandas as gpd
import numpy as np
import folium
from streamlit.components.v1 import html

# Add the root directory to the sys.path
# Here, no check for running interactively -- the streamlit parts cannot be run line-by-line
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils import load_config

# Page configs
st.set_page_config(
    page_title="Coffee farms - Colombia",
    layout='wide'
)

# Load configuration file
config = load_config()
# print(config)

# Page title
st.write("# Map")

# To load vector data
@st.cache_data 
def load_vector(file_path):
    return gpd.read_file(file_path)

# To reproject to a projected geometry
def reproject(gdf):
    return gdf.to_crs(epsg=3857) 
# epsg: 3857 is commonly used for web maps and is the one used in Google maps
# meridonal distances at the poles are amplified -- new standard epsg:4087
# from https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
# TODO investigate other options

# Make sure the working directory is the root folder
# root_path = config['root_path']
# os.chdir(root_path)
# Read in the plots
plots_path = os.path.abspath(config['data_paths']['processed']['coffee_plots'])
# st.write(plots_path)
plots_gdf = load_vector(plots_path)

# Read in the amazonian colombia datapoints
amaz_path = os.path.abspath(config['data_paths']['processed']['amazon'])
amaz_gdf = load_vector(amaz_path)

# Read in radd when in gdf
radd_path = os.path.abspath(config['data_paths']['processed']['radd'])
radd_gdf = load_vector(radd_path)


# Plot vector data on a map
def plot_all_vectors(plots_gdf, vector1_ext_gdf, vector2_ext_gdf, title):
    # Reproject for centroid calculation
    plots_gdf_reproj = reproject(plots_gdf)
    # Create a Folium map centered around the mean coordinates of the geometries
    center = plots_gdf.geometry.centroid.unary_union.centroid.coords[0][::-1] # warning on calculation
    # Because the geometries are small, the geographic CRS is still ok
    
    # Define the map 
    m = folium.Map(location=center, zoom_start=12)

    # Define tooltip for coffee plots
    tooltip_plots = folium.GeoJsonTooltip(fields=list(plots_gdf.columns[:-1]), aliases=[f"{col}:" for col in plots_gdf.columns[:-1]])

    # Define style for coffee plots
    style_plots = {
        'fillColor': '#00000000', #transparent
        'color': '#000000', # black
         'weight': 1, 
    }

    # Add the coffee plots to the Folium map
    folium.GeoJson(plots_gdf, tooltip=tooltip_plots, style_function=lambda x:style_plots, name='Coffee plots').add_to(m)

    # For the second layer
    # Define tooltip for available external vector data
    if vector1_ext_gdf is not None:
        tooltip_vector1_ext_gdf = folium.GeoJsonTooltip(fields=['deforestac'], aliases=['Type: '])
        
        # Define style for external vector layer
        style_vector1_ext_gdf = {
            'fillColor': '#1f77b4', #  blue #FFBF00 amber
            'color': '#1f77b4', 
            'weight': 1.0,
            #'dashArray': "5, 5", # dashes and gaps of 5 units each
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector1_ext_gdf, tooltip=tooltip_vector1_ext_gdf, style_function=lambda x:style_vector1_ext_gdf, name='Amazonian').add_to(m)

    # For the third layer
    # Define tooltip for available external vector data
    if vector2_ext_gdf is not None:
        print('radd_alerts')
        tooltip_vector2_ext_gdf = folium.GeoJsonTooltip(fields=['year', 'conf_level'], aliases=['Year: ', 'Confidence level: '])
        
        # Define style for external vector layer
        style_vector2_ext_gdf = {
            'fillColor': '#ff7f0e', # 
            'color': '#ff7f0e',
            'weight': 1.2,
            #'dashArray': "1, 5", # dots and longer gaps
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector2_ext_gdf, tooltip=tooltip_vector2_ext_gdf, style_function=lambda x:style_vector2_ext_gdf, name='Radd areas').add_to(m)

    # For adding more vector layers, use the structure above


    # Create title HTML
    title_html = f'''
    <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''

    # Add title to the map
    m.get_root().html.add_child(folium.Element(title_html))

    # Add layer control to toggle layers
    folium.LayerControl().add_to(m)

    # Create custom legend
    legend_html = '''
    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; width: 150px; height: 90px; 
        background-color: white; z-index: 9999; font-size: 14px;
        border:2px solid grey; padding: 10px;">
        <b>Legend</b><br>
        <i style="background: #00000000; border: 2px solid black; border-style: solid; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Coffee Farms<br>
        <i style="background: #1f77b4; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
        <i style="background: #ff7f0e; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>RADD<br>
    </div>
    '''
    # The custom legend is based on the arguments passed on the style_function of each GeoJson layer added in folium.
    # Therefore, background, border, border-style might need to be changed if different choices are made in style_function
    # Also, keep in mind that the dimensions of the legend box are based on the current situation. 
    # So, when adding/removing, this will need to be adjusted.

    legend_element = folium.Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Render html representation of the map
    return m._repr_html_()

# Setup to apply filters for years and confidence levels
st.sidebar.header('Please filter RADD alerts here')

# Identify years
unique_year_values = np.sort(radd_gdf['year'].unique())
selected_years = []

# Create a checkbox for each year
st.sidebar.subheader('For the year:')
for year in unique_year_values:
    if st.sidebar.checkbox(f'{year}', key=year, value=True):
        selected_years.append(year)

# Filter data based on selected years
if not selected_years:  # If no checkboxes are selected, show all data
    filtered_year_radd_gdf = radd_gdf
else:
    filtered_year_radd_gdf = radd_gdf[radd_gdf['year'].isin(selected_years)]


# Identify confidence levels
unique_conf_level_values = radd_gdf['conf_level'].unique()
selected_conf_levels = []

# Create a checkbox for each confidence level
st.sidebar.subheader('For the confidence level:')
for conf_level in unique_conf_level_values:
    if st.sidebar.checkbox(f'{conf_level}', key=conf_level, value=True):
        selected_conf_levels.append(conf_level)

# Filter data based on selected confidence levels
if not selected_conf_levels: 
    filtered_year_conf_level_radd_gdf = filtered_year_radd_gdf # After the filter in years is applied
else:
    filtered_year_conf_level_radd_gdf = filtered_year_radd_gdf[filtered_year_radd_gdf['conf_level'].isin(selected_conf_levels)]

# Render map
map_html = plot_all_vectors(plots_gdf=plots_gdf, vector1_ext_gdf=amaz_gdf, vector2_ext_gdf=filtered_year_conf_level_radd_gdf, title='Coffe farms & amazonian Colombia & RADD alerts')
# Display map
html(map_html, width=1000, height=800)



### Alternative ideas ###
# When a different filter type is selected (multiselect)
# spec_year = st.sidebar.multiselect(
#     'Select year:',
#     options = radd_gdf['year'].unique(),
#     default = radd_gdf['year'].unique()
# )
# filtered_year_radd_gdf = radd_gdf.query(
#     'year == @spec_year'
# )
# spec_conf_level = st.sidebar.multiselect(
#     'Select confidence level:',
#     options = radd_gdf['conf_level'].unique(),
#     default = radd_gdf['conf_level'].unique()
# )
# filtered_year_conf_level_radd_gdf = filtered_year_radd_gdf.query(
#     'conf_level == @spec_conf_level'
# )
