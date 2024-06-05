import streamlit as st
import os
import geopandas as gpd
import folium
# from streamlit_folium import folium_static
import rasterio
from rasterio.windows import from_bounds
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from folium.raster_layers import ImageOverlay
from streamlit.components.v1 import html


# ----- Page configs -----
st.set_page_config(
    page_title="Coffee farms - Colombia",
)

# ----- Title of the page -----
st.title("Map")
st.divider()

# Print the current working directory for debugging purposes
# st.write("Current working directory:", os.getcwd())


# Apply custom CSS to increase table column width
st.markdown("""
    <style>
    .dataframe table {
        width: 100% !important;
    }
    .dataframe th, .dataframe td {
        min-width: 200px;
    }
    </style>
""", unsafe_allow_html=True)


# To load vector data
@st.cache_data 
def load_vector(file_path):
    return gpd.read_file(file_path)

# To reproject to a projected geometry
def reproject(gdf):
    return gdf.to_crs(epsg=3857) # epsg: 3857 is commonly used for web maps and is the one used in Google maps
# meridonal distances at the poles are amplified -- new standard epsg:4087
# from https://gis.stackexchange.com/questions/372564/userwarning-when-trying-to-get-centroid-from-a-polygon-geopandas
# TODO investigate other options



#### Load data ####
# Make sure the working directory is the root folder
default_path = "C:\\Users\\user\\Documents\\EAE\\FMT-Progreso"
os.chdir(default_path)

# Read in the coffee plots
#plots_path = "data\\input\\processed\\plots_colombia.geojson"
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
plots_gdf = load_vector(plots_path)

# Read in the amazonian colombia datapoints
amaz_path = os.path.abspath("data\\input\\raw\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp")
amaz_gdf = load_vector(amaz_path)
# Transform as required
amaz_gdf = amaz_gdf.explode(index_parts=True)
# Filtering for only deforestation areas
amaz_gdf = amaz_gdf.loc[amaz_gdf['deforestac'] == 'Perdida']
# Transform the crs based on farms' crs
amaz_gdf = amaz_gdf.to_crs(plots_gdf.crs.to_epsg())

# Read in the raster to gdf radd datapoints
radd_path = os.path.abspath("data\\input\\processed\\radd_gdf.geojson")
radd_gdf = load_vector(radd_path)



# # Display the plots dataset in an expandable table
# with st.expander("Check the complete dataset:"):
#     st.dataframe(plots_gdf)

st.write("Check the coffee farms:")
st.dataframe(plots_gdf.drop(columns='geometry'))
# st.dataframe cannot recognise and show the polygons

# st.write("Check the amazonian colombia dataset:")
# st.dataframe(amaz_gdf.drop(columns='geometry'))

# Plot vector data on a map
def plot_all_vectors(plots_gdf, vector1_ext_gdf, vector2_ext_gdf, title):
    # Reproject for centroid calculation
    plots_gdf_reproj = reproject(plots_gdf)
    # Create a Folium map centered around the mean coordinates of the geometries
    center = plots_gdf.geometry.centroid.unary_union.centroid.coords[0][::-1] # Because the geometries are small, the geographic CRS is still ok
    m = folium.Map(location=center, zoom_start=12)

    # Define tooltip for coffee plots
    tooltip_plots = folium.GeoJsonTooltip(fields=list(plots_gdf.columns[:-1]), aliases=[f"{col}:" for col in plots_gdf.columns[:-1]])

    # Define style for coffee plots
    style_plots = {
        'fillColor': '#0000ff', #blue
        'color': '#0000ff',
    }

    # Add the coffee plots to the Folium map
    folium.GeoJson(plots_gdf, tooltip=tooltip_plots, style_function=lambda x:style_plots, name='Coffee plots').add_to(m)
    #folium.GeoJson(plots_gdf, tooltip=tooltip_plots, name='Coffee plots').add_to(m)

    # For the second layer
    # Define tooltip for available external vector data
    if vector1_ext_gdf is not None:
        tooltip_vector1_ext_gdf = folium.GeoJsonTooltip(fields=list(vector1_ext_gdf.columns[:-1]), aliases=[f"{col}:" for col in vector1_ext_gdf.columns[:-1]])

        # Define style for external vector layer
        style_vector1_ext_gdf = {
            'fillColor': '#000000', #black
            'color': '#000000',
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector1_ext_gdf, tooltip=tooltip_vector1_ext_gdf, style_function=lambda x:style_vector1_ext_gdf, name='Amazonian').add_to(m)
        #folium.GeoJson(vector_ext_gdf, tooltip=tooltip_vector_ext_gdf, name='Amazonian Colombia').add_to(m)

    # For the third layer
    # Define tooltip for available external vector data
    if vector2_ext_gdf is not None:
        print('radd_alerts')
        tooltip_vector2_ext_gdf = folium.GeoJsonTooltip(fields=list(vector2_ext_gdf.columns[:-1]), aliases=[f"{col}:" for col in vector2_ext_gdf.columns[:-1]])

        # Define style for external vector layer
        style_vector2_ext_gdf = {
            'fillColor': '#FF0000', #red
            'color': '#FF0000',
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector2_ext_gdf, tooltip=tooltip_vector2_ext_gdf, style_function=lambda x:style_vector2_ext_gdf, name='Radd areas').add_to(m)



    # # Display the map in Streamlit
    # folium_static(m)

    # Create title HTML
    # title_html = f'''
    # <div style="position: fixed; 
    #             top: 10px; left: 50%; width: 100%; text-align: center;
    #             font-size: 24px; font-weight: bold; color: black;">
    #     {title}
    # </div>
    # '''

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
        <i style="background: #0000ff; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Coffee Farms<br>
        <i style="background: #000000; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
        <i style="background: #FF0000; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>RADD<br>
    </div>
    '''
    legend_element = folium.Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Render Folium map as HTML
    map_html = m._repr_html_()
    html(map_html, width=1000, height=700)

plot_all_vectors(plots_gdf=plots_gdf, vector1_ext_gdf=amaz_gdf, vector2_ext_gdf=radd_gdf, title='Coffe farms & amazonian Colombia & RADD alerts')