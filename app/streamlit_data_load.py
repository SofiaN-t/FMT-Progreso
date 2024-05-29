import streamlit as st
import geopandas as gpd

# To load vector data
@st.cache_data 
def load_vector(file_path):
    return gpd.read_file(file_path)