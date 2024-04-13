# Overlap function

---

## Row-by-row operation
Here, all polygons of one file are checked for intersection against all polygons of the other file. It seems to be computationally expensive and it returns an index for the geojson file when an intersection exists and nothing when it doesn't.

## Spatial join
Is a key operation in spatial analysis that combines two GeoDataFrames based on their spatial relationship. It merges data from one set of geographical features with another set based on ther locations and spatial interaction.

Spatial interactions include 'intersects', 'within', 'contains', 'touches', 'overlaps'. For a detailed explanation, check below.

It is computationally less expensive because of the way it operates. When it is required, Geopandas creates indices that represent the bounding boxes of the geometries (bounding boxes are the minima and maxima of the x and y coordinates of each geometry). When those do not satisfy the spatial relationship in question, the particular geometries will not. This step significantly reduces the number of detailed geometric calculations needed.

When a spatial relationship is found to be satisfied, Geopandas merges the correspoding rows from each Geodataframe. Thus, the sjoin function returns a new Geodataframe that includes combined data from both input frames for the pairs of geometries that meet the criteria.

---

# Spatial relationships
How geometries can relate to each other.

## Intersects
Returns True if the boundaries and/or interiors of the two geometries intersect in any way.

## Within
Returns True if one geometry is completely inside another.

## Contains
Returns True if one geometry completely contains another.

## Touches
Returns True if two geometries have at least one point in common, but their interiors do not intersect.

## Overlaps
Returns True if the geometries share some but not all points in common and the intersection of their interiors has the same dimension as the geometries themselves.

