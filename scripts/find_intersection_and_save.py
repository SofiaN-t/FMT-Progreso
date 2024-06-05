import os
import geopandas as gpd
import pandas as pd


# Load the data
plots_path = os.path.abspath("data\\input\\processed\\plots_colombia.geojson")
amaz_path = os.path.abspath("data\\input\\processed\\amaz_gdf.geojson")
radd_path = os.path.abspath("data\\input\\processed\\radd_gdf.geojson")

plots_gdf = gpd.read_file(plots_path)
radd_gdf = gpd.read_file(radd_path)
amaz_gdf = gpd.read_file(amaz_path)
amaz_gdf = amaz_gdf.to_crs(plots_gdf.crs.to_epsg())

# Combine alerts
gdf_alerts = gpd.GeoDataFrame(pd.concat([radd_gdf, amaz_gdf], ignore_index=True))
gdf_alerts['source'] = ['radd_gdf']*len(radd_gdf) + ['amaz_gdf']*len(amaz_gdf)

# t_df = gdf_alerts.pivot(index='source', columns=['value', 'year', 'conf_level', 'geometry', 'level_1', 'deforestac'])
# t_df.head()

# To define intersection
def find_intersection(gpd1, gpd2):
    check_overlap = gpd.sjoin(gpd1, gpd2, how="inner", predicate='intersects')
    if check_overlap.shape[0] > 0:
        # Find the intersection
        intersection_result = check_overlap.drop(['geometry', 'index_right', 'value', 'year', 'level_1', 'deforestac'], axis=1) # removing unnecessary columns
        # Pivot the table to have the source column as two different ones
        intersection_result = intersection_result.pivot(columns='source')
    else:
        helper_df = pd.DataFrame(data={'Amazonian': ['No intersection'] * gpd1.shape[0],
                                                 'RADD': ['No intersection'] * gpd1.shape[0]})
        intersection_result = pd.concat([gpd1.drop(['geometry'], axis=1), helper_df], axis=1)
    return intersection_result

# Find intersection
intersection_df = find_intersection(plots_gdf, gdf_alerts)
# Save to file
intersection_df.to_csv('data/input/processed/intersection.csv')