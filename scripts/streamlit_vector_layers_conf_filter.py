import streamlit as st
import os
import geopandas as gpd
import numpy as np
import folium
# from streamlit_folium import folium_static
from streamlit.components.v1 import html


# ----- Page configs -----
st.set_page_config(
    page_title="Coffee farms - Colombia",
)

# ----- Left menu -----
# with st.sidebar:
#     st.image("eae_img.png", width=200)
#     st.header("Introduction to Programming Languages for Data")
#     st.write("###")
#     st.write("***Final Project - Dec 2023***")
#     st.write(f"**Author:** {name}")
#     st.write("**Instructor:** [Enric Domingo](https://github.com/enricd)")




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

# Make sure the working directory is the root folder
default_path = "C:\\Users\\user\\Documents\\EAE\\FMT-Progreso"
os.chdir(default_path)
# Read in the plots
#plots_path = "data\\input\\processed\\plots_colombia.geojson"
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
plots_gdf = load_vector(plots_path)

# Read in the amazonian colombia datapoints
amaz_path = os.path.abspath("data\\input\\processed\\amaz_gdf.geojson")
amaz_gdf = load_vector(amaz_path)

# Read in radd when in gdf
radd_path = os.path.abspath("data\\input\\processed\\radd_gdf.geojson")
radd_gdf = load_vector(radd_path)

# # Display the plots dataset in an expandable table
# with st.expander("Check the complete dataset:"):
#     st.dataframe(plots_gdf)

# st.write("Check the coffee farms:")
# st.dataframe(plots_gdf.drop(columns='geometry'))
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
        'fillColor': '#00000000', #transparent
        'color': '#000000', # black
         'weight': 1, 
    }

    # Add the coffee plots to the Folium map
    folium.GeoJson(plots_gdf, tooltip=tooltip_plots, style_function=lambda x:style_plots, name='Coffee plots').add_to(m)
    #folium.GeoJson(plots_gdf, tooltip=tooltip_plots, name='Coffee plots').add_to(m)

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
        #folium.GeoJson(vector_ext_gdf, tooltip=tooltip_vector_ext_gdf, name='Amazonian Colombia').add_to(m)

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
        <i style="background: #00000000; border: 2px solid black; border-style: solid; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Coffee Farms<br>
        <i style="background: #1f77b4; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
        <i style="background: #ff7f0e; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>RADD<br>
    </div>
    '''
    # legend_html = '''
    # <div style="
    #     position: fixed; 
    #     bottom: 50px; left: 50px; width: 150px; height: 90px; 
    #     background-color: white; z-index: 9999; font-size: 14px;
    #     border:2px solid grey; padding: 10px;">
    #     <b>Legend</b><br>
    #     <i style="background: #00000000; border: 2px solid black; border-style: solid; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Coffee Farms<br>
    #     <i style="background: #FFBF00; border: 2px dashed black; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
    #     <i style="background: #FFBF00; border: 2px dotted black; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>RADD<br>
    # </div>
    # '''
    legend_element = folium.Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Render html representation of the map
    return m._repr_html_()
    # map_html = m._repr_html_()
    # html(map_html, width=1000, height=700)


# Apply filters for years
unique_values_year = radd_gdf['year'].unique()
filter_value_year = st.selectbox('Filter RADD alerts by year:', ['All'] + list(unique_values_year))

# Apply filters for confidence level
unique_values_conf = radd_gdf['conf_level'].unique()
filter_value_conf = st.selectbox('Filter RADD alerts by confidence level:', ['All'] + list(unique_values_conf))

if filter_value_year == 'All':
    filtered_radd_gdf = radd_gdf
    if filter_value_conf == 'All':
        filtered_radd_gdf = radd_gdf
    else:
        filtered_radd_gdf = radd_gdf[radd_gdf['conf_level'] == filter_value_conf]
else:
    filtered_radd_gdf = radd_gdf[radd_gdf['year'] == filter_value_year]
    if filter_value_conf == 'All':
        filtered_radd_gdf = filtered_radd_gdf
    else:
        filtered_radd_gdf = filtered_radd_gdf[filtered_radd_gdf['conf_level'] == filter_value_conf]

# Render map
map_html = plot_all_vectors(plots_gdf=plots_gdf, vector1_ext_gdf=amaz_gdf, vector2_ext_gdf=filtered_radd_gdf, title='Coffe farms & amazonian Colombia & RADD alerts')
# Display map
html(map_html, width=1000, height=800)

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
