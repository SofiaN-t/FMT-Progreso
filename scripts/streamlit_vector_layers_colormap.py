import streamlit as st
import os
import geopandas as gpd
import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
import numpy as np
import folium
# from streamlit_folium import folium_static
from branca.element import MacroElement
from jinja2 import Template
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



## Functions for plot ##
# Define a list of unique values for confidence level
unique_values = radd_gdf['conf_level'].unique()

# Create a colormap for these unique values
if len(unique_values) == 2:
    colors = ['#1f77b4', '#ff7f0e']  # Example: blue and orange
else:
    cmap = plt.cm.get_cmap('coolwarm', len(unique_values))
    colors = [mcolors.rgb2hex(cmap(i)) for i in range(cmap.N)]

# Map text values to colors
value_to_color = {str(k): v for k, v in zip(unique_values, colors)}


# Function to determine color based on confidence level
def style_function(feature):
    value = feature['properties']['conf_level']
    return {
        'fillColor': value_to_color[value],
        'color': value_to_color[value],  
        'weight': 1.0, # no border color
        'fillOpacity': 0.8,
    }
# def style_function(feature):
#     value = feature['properties']['conf_level']  # Extract the value of the 'value' property
#     color = value_to_color.get(value, '#FFFFFF')  # Get the corresponding color or default to white
#     # Print each feature's style for debugging
#     st.write("Feature value:", value, "Color:", color)
#     return {
#         'fillColor': color,  # Set fill color
#         'color': color,       # No border color
#         'weight': 1.0,        
#         'fillOpacity': 1.0   # Set fill opacity
#     }

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
        tooltip_vector1_ext_gdf = folium.GeoJsonTooltip(fields=['deforestac'], aliases=['type: '])
        
        # Define style for external vector layer
        style_vector1_ext_gdf = {
            'fillColor': '#FF00FF', # magenta
            'color': '#FF00FF', 
            'weight': 1,
            'fillOpacity': 1.0,
            #'dashArray': "5, 5", # dashes and gaps of 5 units each
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector1_ext_gdf, tooltip=tooltip_vector1_ext_gdf, style_function=lambda x:style_vector1_ext_gdf, name='Amazonian').add_to(m)
        #folium.GeoJson(vector_ext_gdf, tooltip=tooltip_vector_ext_gdf, name='Amazonian Colombia').add_to(m)

    # For the third layer
    # Define tooltip for available external vector data
    if vector2_ext_gdf is not None:
        print('radd_alerts')
        tooltip_vector2_ext_gdf = folium.GeoJsonTooltip(fields=['year'], aliases=['Year'])
        
        # Style defined separately as colormap

        # Add the external vector layer to the Folium map
        folium.GeoJson(vector2_ext_gdf, tooltip=tooltip_vector2_ext_gdf, style_function=style_function, name='Radd alerts').add_to(m)

    
    
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
    # legend_html = '''
    # {% macro html(this, kwargs) %}
    # <div style="
    #     position: fixed; 
    #     bottom: 50px; left: 50px; width: 150px; height: 90px; 
    #     background-color: white; z-index: 9999; font-size: 14px;
    #     border:2px solid grey; padding: 10px;">
    #     <b>Legend</b><br>
    #     <i style="background: #00000000; border: 1px solid black; border-style: solid; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Coffee Farms<br>
    #     <i style="background: #FF00FF; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
    #     {% for value, color in value_to_color.items() %}
    #         <i style="background:{{ color }}; width:20px; height:20px; float:left; margin-right:5px; opacity:0.7;"></i>{{ value }}<br>
    #     {% endfor %}
    # </div>
    # {% endmacro %}
    # '''
    # legend_html = '''
    # <div style="
    #     position: fixed; 
    #     bottom: 50px; left: 50px; width: 150px; height: auto; 
    #     border:2px solid grey; z-index:9999; font-size:14px;
    #     ">
    #     <div style="background-color:white; padding:10px;">
    #         <b>Color Legend</b><br>
    #         {content}
    #     </div>
    # </div>
    # '''

    # Generate the legend for coffee plots
    layer_plots_content = '<i style="background: #FFBF00; border: 2px solid black; width: 18px; height: 18px; float: left; margin-right: 5px;"></i>Coffee Farms<br>'

    # Generate the legend for amazonian
    layer_amaz_content = '<i style="background: #FF00FF; width: 18px; height: 18px; float: left; margin-right: 5px;"></i>Amazonian<br>'

    # Generate the legend HTML for radd
    layer_radd_items = ''.join([f'<i style="background:{color}; width:18px; height:18px; float:left; margin-right:5px; opacity:0.7;"></i>{value}<br>' for value, color in value_to_color.items()])
    layer_radd_content = f'<b>Layer 3</b><br>{layer_radd_items}'

    # Combine the legends
    combined_legend_html = f'''
    <div style="
        position: fixed; 
        bottom: 50px; 
        left: 50px; 
        width: 200px; 
        height: auto; 
        border: 2px solid grey; 
        z-index: 9999; 
        font-size: 14px; 
        background-color: white; 
        padding: 10px;">
        <b>Legend</b><br>
        <div>
            <b>Layer 1</b><br>
            {layer_plots_content}
        </div>
        <div style="margin-top: 10px;">
            <b>Layer 2</b><br>
            {layer_amaz_content}
        </div>
        <div style="margin-top: 10px;">
            <b>Layer 3</b><br>
            {layer_radd_content}
        </div>
    </div>
    '''
    # Display the combined legend HTML for debugging
    st.write(combined_legend_html)

    # Create a MacroElement with the combined legend
    legend = MacroElement()
    legend._template = Template(combined_legend_html)

    # Add the legend to the map
    m.get_root().add_child(legend)

    # Render html representation of the map
    return m._repr_html_()
    # map_html = m._repr_html_()
    # html(map_html, width=1000, height=700)


# Apply filters for years
unique_values = radd_gdf['year'].unique()
filter_value = st.selectbox('Filter RADD alerts by year:', ['All'] + list(unique_values))

if filter_value == 'All':
    filtered_radd_gdf = radd_gdf
else:
    filtered_radd_gdf = radd_gdf[radd_gdf['year'] == filter_value]

# Render map
map_html = plot_all_vectors(plots_gdf=plots_gdf, vector1_ext_gdf=amaz_gdf, vector2_ext_gdf=filtered_radd_gdf, title='Coffe farms & amazonian Colombia & RADD alerts')
# Display map
html(map_html, width=1000, height=700)

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
