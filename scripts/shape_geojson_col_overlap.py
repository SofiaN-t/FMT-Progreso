## Libraries ##
import geopandas as gpd
import matplotlib.pyplot as plt

## Read files ##
# geojson
# path
geojsonfile_path = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
# file
geojson_gdf = gpd.read_file(geojsonfile_path)

# shapefile
# path
shapefile_path = "C:\\Users\\user\\Documents\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp"
# file
shapefile_gdf = gpd.read_file(shapefile_path)
shapefile_gdf.columns.values
shapefile_gdf.head()
shapefile_gdf.geom_type.unique()
shapefile_gdf.crs
# shapefile_gdf.describe()
### Observations: ###
# For the shapefile to be read, you also need all of the rest required files 
# When printing the head, last col indicates multipolygons io polygons -- will have to be treated
# deforestac column includes other events, not only lost forest -- will have to be filtered
# geometry = 'polygons'
# coordinate system = 
shapefile_gdf = shapefile_gdf.explode()
shapefile_gdf = shapefile_gdf.loc[shapefile_gdf['deforestac'] == 'Perdida']
shapefile_gdf.head()
shapefile_gdf['deforestac'].unique()
# Succesfully transformed from multipolygon to polygons
# Succesfully filtered for lost forest

# Plot the shapefile
shapefile_gdf.plot()
plt.show()


# Function to check overlap
# Assuming you want to check if any polygon in the GeoJSON overlaps with any polygon in the shapefile
# Loop through each geometry in one GeoDataFrame and check against all in the other
count=0
for index, geojson_geom in geojson_gdf.iterrows():
    for _, shapefile_geom in shapefile_gdf.iterrows():
        count = count + 1
        if geojson_geom.geometry.intersects(shapefile_geom.geometry):
            print(f"Overlap found between polygons at GeoJSON index {index} and shapefile.")
        # else:
        #     print("No overlap")
print(count)
## Observations: ##
# There does not seem to be some overlap 
# There are 552468 combinations checked