## Libraries ##
import geopandas as gpd
import geoplot
import geoplot.crs as gcrs
import matplotlib.pyplot as plt

## Read created geojson file ##
df = gpd.read_file("data\\raw\\output\\Polygons_EAE_project_Progreso.geojson")
df.head()
df.crs

## Plot ##
geoplot.polyplot(df, projection=gcrs.AlbersEqualArea(), 
                 edgecolor='darkgrey', facecolor='lightgrey', 
                 linewidth=.3, figsize=(12, 8)
                 )
plt.show()

# Alternatively,
df.plot()
plt.show()
### Observations: ###
# polyplot as it is here, does not show coordinates on plot but on the hover over
# Also, longitude is for one positive and for the other negative TODO
