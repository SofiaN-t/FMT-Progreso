import geopandas as gpd

# Load the single polygon GeoJSON file
polygon1_path = 'data/raw/polygon1.geojson'
polygon1_gdf = gpd.read_file(polygon1_path)

# Load the Deforestation Alerts GeoJSON file
alerts_path = 'data\download\Deforestation_alerts_(RADD).geojson'
alerts_gdf = gpd.read_file(alerts_path)

# Ensure both GeoDataFrames use the same Coordinate Reference System (CRS)
if polygon1_gdf.crs != alerts_gdf.crs:
    polygon1_gdf = polygon1_gdf.to_crs(alerts_gdf.crs)

# Check for overlaps using the intersects method
# We assume 'polygon1_gdf' contains only one polygon
polygon1 = polygon1_gdf.iloc[0].geometry
overlaps = alerts_gdf[alerts_gdf.intersects(polygon1)]

# Print the result
if overlaps.empty:
    print("The polygon from 'polygon1.geojson' does not overlap with any polygons in 'Deforestation_alerts_RADD.geojson'.")
else:
    print(f"There are {len(overlaps)} overlapping polygons. Here are their details:")
    print(overlaps)
