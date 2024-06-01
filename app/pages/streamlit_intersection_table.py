import streamlit as st
import geopandas as gpd
import os
import pandas as pd
from streamlit_data_functions import load_vector
from streamlit_data_functions import find_intersection


# Load the data
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
amaz_path = os.path.abspath("data\\input\\raw\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp")
radd_path = os.path.abspath("data\\input\\processed\\radd_gdf.geojson")

plots_gdf = load_vector(plots_path)
radd_gdf = load_vector(radd_path)
amaz_gdf = load_vector(amaz_path)
amaz_gdf = amaz_gdf.to_crs(plots_gdf.crs.to_epsg())

# Find intersection with both
# First, combine alerts
gdf_alerts = gpd.GeoDataFrame(pd.concat([radd_gdf, amaz_gdf], ignore_index=True))
gdf_alerts['source'] = ['radd_gdf']*len(radd_gdf) + ['amaz_gdf']*len(amaz_gdf)

print_gdf = find_intersection(plots_gdf, gdf_alerts)

# Write the table
def write_table(gdf):
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

    # plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
    # plots_gdf = load_vector(plots_path)

    st.write("Check the coffee farms:")
    st.dataframe(gdf)

write_table(print_gdf)