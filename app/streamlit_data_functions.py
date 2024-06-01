import streamlit as st
import geopandas as gpd
import folium
# from streamlit_folium import folium_static
from streamlit.components.v1 import html
import pandas as pd


# To load vector data
@st.cache_data 
def load_vector(file_path):
    return gpd.read_file(file_path)


# To plot vector data on a map
def plot_all_vectors(plots_gdf, vector1_ext_gdf, vector2_ext_gdf, title):
    # Reproject for centroid calculation
    #plots_gdf_reproj = reproject(plots_gdf)
    # Create a Folium map centered around the mean coordinates of the geometries
    center = plots_gdf.geometry.centroid.unary_union.centroid.coords[0][::-1] # Because the geometries are small, the geographic CRS is still ok
    m = folium.Map(location=center, zoom_start=12)

    # Define tooltip for coffee plots
    tooltip_plots = folium.GeoJsonTooltip(fields=list(plots_gdf.columns[:-1]), aliases=[f"{col}:" for col in plots_gdf.columns[:-1]])

    # Define style for coffee plots
    style_plots = {
        'fillColor': '#00000000', #transparent
        'color': '#000000', # black
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
            'fillColor': '#FFBF00', # amber
            'color': '#000000', #black
            'weight': 1,
            'dashArray': "5, 5", # dashes and gaps of 5 units each
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
            'fillColor': '#FFBF00', 
            'color': '#000000',
            'weight': 1,
            'dashArray': "1, 5", # dots and longer gaps
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
        <i style="background: #FFBF00; border: 2px dashed black; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>Amazonian<br>
        <i style="background: #FFBF00; border: 2px dotted black; width: 18px; height: 18px; float: left; margin-right: 8px;"></i>RADD<br>
    </div>
    '''
    legend_element = folium.Element(legend_html)
    m.get_root().html.add_child(legend_element)

    # Render Folium map as HTML
    map_html = m._repr_html_()
    html(map_html, width=1000, height=700)


# To find intersections (if any)
def find_intersection(gpd1, gpd2):
    check_overlap = gpd.sjoin(gpd1, gpd2, how="inner", predicate='intersects')
    if check_overlap.shape[0] > 0:
        intersection_result = check_overlap
    else:
        intersection_result = pd.DataFrame(data={'col': ['No intersection']})
    return intersection_result