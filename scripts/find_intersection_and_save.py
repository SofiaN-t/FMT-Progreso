## Libraries ##
import sys
import os
import geopandas as gpd
import pandas as pd

# Check if running in an interactive environment eg when running line-by-line
def is_interactive():
    import __main__ as main
    return not hasattr(main, '__file__')

# Add the root directory to the sys.path if not running interactively
if not is_interactive():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load configuration file
from utils import load_config
config = load_config()

# Load the data
plots_path = os.path.abspath(config['data_paths']['processed']['coffee_plots'])
amaz_path = os.path.abspath(config['data_paths']['processed']['amazon'])
radd_path = os.path.abspath(config['data_paths']['processed']['radd'])

plots_gdf = gpd.read_file(plots_path)
radd_gdf = gpd.read_file(radd_path)
amaz_gdf = gpd.read_file(amaz_path)

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
        check_overlap['intersecting_with'] = 'Unknown' # Adding more informative column
        check_overlap.loc[check_overlap['source'] == 'radd_gdf', 'intersecting_with'] = 'RADD'
        check_overlap.loc[check_overlap['source'] == 'amaz_gdf', 'intersecting_with'] = 'Amazonian'
        intersection_result = check_overlap.drop(['geometry', 'value', 'year', 'level_1', 'deforestac', 'source'], axis=1) # removing unnecessary columns
        # Here, index_right includes the index of the alerts geodataframe with which the corresponding coffee plot intersects
    else:
        helper_df = pd.DataFrame(data={'Amazonian': ['No intersection'] * gpd1.shape[0],
                                                 'RADD': ['No intersection'] * gpd1.shape[0]})
        intersection_result = pd.concat([gpd1.drop(['geometry'], axis=1), helper_df], axis=1)
    return intersection_result

# Find intersection
intersection_df = find_intersection(plots_gdf, gdf_alerts)
# Save to file
intersection_path = config['data_paths']['processed']['intersection']
intersection_df.to_csv(intersection_path)