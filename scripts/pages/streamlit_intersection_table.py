import streamlit as st
import os
import geopandas as gpd
from streamlit_vector_layers import load_vector


# ----- Title of the page -----
st.title("Interesections with deforestation alerts")
st.divider()

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

plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
plots_gdf = load_vector(plots_path)

st.write("Check the coffee farms:")
st.dataframe(plots_gdf.drop(columns='geometry'))