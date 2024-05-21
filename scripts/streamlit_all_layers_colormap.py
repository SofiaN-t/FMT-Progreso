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
from matplotlib import cm
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
# Doesn't seem to be working #TODO

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

# To load raster data (based on window)
def read_radd_window(file_path, bounds, only_alerts):
    with rasterio.open(file_path) as src:
        # Convert geographic to pixel coordinates
        window = from_bounds(*bounds, src.transform)
        # Read the window
        data = src.read(1, window=window)
        if only_alerts == True:
            # Keep only alerts (non-negative values)
            data = np.where(data > 0, data, np.nan)
        else:
            data = data
        # Get the transform of window to be able to map pixel to geographic
        transform = src.window_transform(window)
        return data, transform 

# To convert raster data to an image format suitable for folium
def array_to_image(data):
    data_normalized = (data - np.min(data)) / (np.max(data) - np.min(data))
    return np.uint8(data_normalized * 255)
# This ends up plotting a black rectangular - ??

# To convert raster data to an RGBA image with a colormap
def apply_colormap(data):
    norm = Normalize(vmin=np.min(data), vmax=np.max(data))
    cmap = plt.get_cmap('viridis')  # Choose a colormap
    mappable = ScalarMappable(norm=norm, cmap=cmap)
    rgba_image = mappable.to_rgba(data, bytes=True)
    return rgba_image





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

## Read in the radd data (raster)
# Path for raster
radd_path = os.path.abspath('data/input/raw/10N_080W.tif')
# Define bounds for reading window: expected format (min_lon, min_lat, max_lon, max_lat)
image_bounds = (-76.5, 1.8, -75.5, 2) 
# Define whether you want to show only the alerts
only_alerts = False
radd_data, radd_transform = read_radd_window(file_path=radd_path, bounds=image_bounds, only_alerts=only_alerts)
# Convert raster data to a suitable format
# radd_data = apply_colormap(data=radd_data)
radd_data = array_to_image(data=radd_data)





# # Display the plots dataset in an expandable table
# with st.expander("Check the complete dataset:"):
#     st.dataframe(plots_gdf)

st.write("Check the coffee farms:")
st.dataframe(plots_gdf.drop(columns='geometry'))
# st.dataframe cannot recognise and show the polygons

# st.write("Check the amazonian colombia dataset:")
# st.dataframe(amaz_gdf.drop(columns='geometry'))

# Plot all data on a map
def plot_vector_and_raster(plots_gdf, vector_ext_gdf, raster_ext, title):
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


    # Define tooltip for available external vector data
    if vector_ext_gdf is not None:
        tooltip_vector_ext_gdf = folium.GeoJsonTooltip(fields=list(vector_ext_gdf.columns[:-1]), aliases=[f"{col}:" for col in vector_ext_gdf.columns[:-1]])
        
        # Define style for external vector layer
        style_vector_ext_gdf = {
            'fillColor': '#000000', #black
            'color': '#000000',
        }
        # Add the external vector layer to the Folium map
        folium.GeoJson(vector_ext_gdf, tooltip=tooltip_vector_ext_gdf, style_function=lambda x:style_vector_ext_gdf, name='Amazonian Colombia').add_to(m)
        #folium.GeoJson(vector_ext_gdf, tooltip=tooltip_vector_ext_gdf, name='Amazonian Colombia').add_to(m)

        # Raster data
        # Reformulate the bounds to match ImageOverlay: expected [[min_lat, min_lon], [max_lat, max_lon]]
        folium_bounds = [[image_bounds[1], image_bounds[0]], [image_bounds[3], image_bounds[2]]]

        # Add external raster layer as an overlay
        ImageOverlay(image=raster_ext, bounds=folium_bounds, name='RADD data', colormap=cm.get_cmap('Oranges', 10)).add_to(m)
    
    
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
        <i style="background: #000000; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian Colombia
    </div>
    '''
    legend_element = folium.Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Render Folium map as HTML
    map_html = m._repr_html_()
    html(map_html, width=1000, height=700)

plot_vector_and_raster(plots_gdf=plots_gdf, vector_ext_gdf=amaz_gdf, raster_ext=radd_data, title='Coffe farms & amazonian Colombia alerts')


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
