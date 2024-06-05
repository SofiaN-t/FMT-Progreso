import streamlit as st
import geopandas as gpd
import os
import pandas as pd


st.set_page_config(
    page_title="Coffee farms intersections - Colombia",
    layout='wide'
)

# Load the intersection table data
intersection_path = 'data/input/processed/intersection.csv'
intersection_df = pd.read_csv(intersection_path, index_col=0)

# Write the table
def write_table(df):
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

    st.header("Check the potential intersections:")
    if df.shape[0] > 4:
        st.write('These are the farms that overlap with the deforested areas:')
    st.dataframe(df)

write_table(intersection_df)