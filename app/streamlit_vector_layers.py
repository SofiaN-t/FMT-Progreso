import streamlit as st
import os
import geopandas as gpd
import folium
# from streamlit_folium import folium_static
from streamlit.components.v1 import html

from streamlit_data_functions import load_vector
from streamlit_data_functions import plot_all_vectors

from pages import streamlit_intersection_table


# ----- Page configs -----
# Page navigation
# st.sidebar.title("Navigation")
# page = st.sidebar.radio("Select a page", ["Map", "Table"], index=0)

# 
# Load the data
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
amaz_path = os.path.abspath("data\\input\\raw\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp")
radd_path = os.path.abspath("data\\input\\processed\\radd_gdf.geojson")

plots_gdf = load_vector(plots_path)
amaz_gdf = load_vector(amaz_path)
radd_gdf = load_vector(radd_path)

# Plot map
plot_all_vectors(plots_gdf, amaz_gdf, radd_gdf, 'map')

# if page == 'Map':
#     st.title("Map")
#     plots_gdf = load_vector(plots_path)
#     print('plots loaded')
#     # amaz_gdf = load_vector(amaz_path)
#     amaz_gdf = None
#     # print('amaz loaded')
#     radd_gdf = load_vector(radd_path)
#     print('radd loaded')
#     plot_all_vectors(plots_gdf, amaz_gdf, radd_gdf, 'map')
# elif page == 'Table':
#     st.title("Interesections with deforestation alerts")
#     streamlit_intersection_table.write_table(load_vector(plots_path))


# def main():
#     st.title("GeoJSON Plotter")

#     # File uploader to upload a GeoJSON file
#     geojson_file = st.file_uploader("Upload GeoJSON file", type=["geojson"])
    
#     if geojson_file:
#         # Load the GeoJSON data
#         gdf = load_geojson(geojson_file)
        
#         # Display the data
#         st.write("GeoDataFrame:", gdf)
        
#         # Plot the GeoJSON data
#         plot_geojson(gdf)

# if __name__ == "__main__":
#     main()
