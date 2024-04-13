## Libraries ##
import geopandas as gpd
import matplotlib.pyplot as plt

## Read files ##
# geojson
# path
geojsonfile_path = "data\\raw\\output\\Polygons_EAE_project_Progreso.geojson"
# file
geojson_gdf = gpd.read_file(geojsonfile_path)
geojson_gdf.info()
geojson_gdf.crs
# Keep the epsg based on observations on the other file
geojson_gdf_epsg = geojson_gdf.crs.to_epsg()
# Check shape
geojson_gdf.shape[0] #42

# shapefile
# path
shapefile_path = "C:\\Users\\user\\Documents\\perdida_de_bosque\\TMAPB_Region_100K_2020_2022.shp"
# file
shapefile_gdf = gpd.read_file(shapefile_path)
shapefile_gdf.info()
shapefile_gdf.head()
shapefile_gdf.geom_type.unique()
shapefile_gdf.crs
# shapefile_gdf.describe()
shapefile_gdf.shape[0]
### Observations: ###
# For the shapefile to be read, you also need all of the rest required files 
# When printing the head, last col indicates multipolygons io polygons -- will have to be treated
# deforestac column includes other events, not only lost forest -- will have to be filtered
# geometry = 'polygons'
# coordinate system is different than the one for the geojson file

# From multipolygons to polygons
shapefile_gdf = shapefile_gdf.explode()

# Filtering for only deforestation areas
shapefile_gdf = shapefile_gdf.loc[shapefile_gdf['deforestac'] == 'Perdida']

# Transform the crs based on farms' crs
shapefile_gdf = shapefile_gdf.to_crs(geojson_gdf_epsg)

shapefile_gdf.head()
shapefile_gdf['deforestac'].unique()
shapefile_gdf.crs
# Succesfully transformed from multipolygon to polygons
# Succesfully filtered for lost forest
# Successfully transformed crs


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
# There are 552468 (42*13154) combinations checked

# Alternatively, less computationally expensive
check_overlap = gpd.sjoin(geojson_gdf, shapefile_gdf, how="inner", op='intersects')
# It returns an empty dataframe, hence here there is also no overlap