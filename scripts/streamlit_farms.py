import streamlit as st
import os
import geopandas as gpd
import folium
# from streamlit_folium import folium_static
from streamlit.components.v1 import html


# ----- Page configs -----
st.set_page_config(
    page_title="Coffee farms - Colombia",
)

# ----- Title of the page -----
st.title("Coffe farms")
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


# Load farms data
@st.cache_data 
def load_vector(file_path):
    return gpd.read_file(file_path)

# Make sure the working directory is the root folder
default_path = "C:\\Users\\user\\Documents\\EAE\\FMT-Progreso"
os.chdir(default_path)
#plots_path = "data\\input\\processed\\plots_colombia.geojson"
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
plots_gdf = load_vector(plots_path)

# # Display the plots dataset in an expandable table
# with st.expander("Check the complete dataset:"):
#     st.dataframe(plots_gdf)

st.write("Check the coffee farms:")
st.dataframe(plots_gdf.drop(columns='geometry'))
# st.dataframe cannot recognise and show the polygons

# Plot GeoJSON data on a map
def plot_vector(gdf, title):
    # Create a Folium map centered around the mean coordinates of the geometries
    center = gdf.geometry.centroid.unary_union.centroid.coords[0][::-1]
    m = folium.Map(location=center, zoom_start=12)

    # Add the GeoDataFrame to the Folium map
    folium.GeoJson(gdf).add_to(m)

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

    title_html = f'''
    <h3 align="center" style="font-size:16px"><b>{title}</b></h3>
    '''

    # Add title to the map
    m.get_root().html.add_child(folium.Element(title_html))

    # Render Folium map as HTML
    map_html = m._repr_html_()
    html(map_html, width=1000, height=700)

plot_vector(plots_gdf, "Coffee farms")


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
