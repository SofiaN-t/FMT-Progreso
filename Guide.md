# Introduction
This tool is designed to visually represent a map with three distinct layers, enabling users to identify potential intersections with deforested areas in coffee-producing regions of the department of Huila in Colombia. By leveraging this tool, stakeholders can assess the risk of coffee farms being situated within or in the proximity of deforested areas and consequently be effectively informed on whether coffee exports from these areas align with EU regulations. 

It consists of two main pages. The first one includes an interactive map visualizing the different layers with filtering functionalities. The second page informs the user on intersections on a coffee farm basis via a tabular view. 


# Prerequisites
- Software requirements -- probably not necessary

# Installation
- Environment setup: instructions to set up virtual environment

# Data
- Mention the structure of the project and potentially what is where -- ?? Think about it again

# Data processing
After having setup the environment, the files used for the dashboard need to be produced. To ensure reproducibility, an adjustment to some file paths needs to be made. Currently, 'config.json' specifies the root and the data folder paths. If the zip file is unpacked as is, the data paths should remain the same. Although not strictly used, we suggest that the root_path is changed to the root directory of the project. When a different folder structure is desired, the configuration will need to be changed to reflect the new structure.

With these changes, we proceed to explain the developed scripts and the order in which they need to run.

1. 'transform_provided_raw_file.py' is the script that needs to run first. It produces a geojson file with the available relevant information for the provided coffee plots. In this case, an excel file is the input for the script (data/input/raw/plots_colombia.xlsx). We assume that any provided file with information on the coffee farms will be of similar if not the same format (since it was provided by Progreso). After some basic manipulation, a geojson file is produced and saved (data/input/processes/plots_colombia.geojson). This file contains vector data which is a geographic data type where data is stored as a collection of points, lines, or polygons as pairs of (x,y) coordinates along with other non-spatial related attributes. Geojson is a typical format for geospatial data and is easy to be read and transformed with a standard for geospatial applications library, geopandas (which draws from pandas).
This file will be used later both for further development and for the dashboard. 

To run the script at once: 
1. Open a terminal
2. Navigate (with cd <path/to/the/project_folder>) to the folder where you store this code
3. Activate the virtual environment (if applicable) with <env_name>\Scripts\activate.bat on Windows
4. Type python scripts\transform_provided_raw_file.py
You should be able to find a file titled 'plots_colombia.geojson' in the folder path data\input\processed.

Alternatively, you can run the code line-by-line.

2. 'read_open_source_data.py' should run, next. It produces two geojson files having as sources two open-source datasets.

First, a dataset for the Amazonian Colombia alerts (data/input/raw/perdida_de_bosque/TMAPB_Region_100K_2020_2022.shp) is loaded. Please be informed that the other files in the same folder might be necessary for the reading of this dataset. The dataset is, then, transformed to a desirable format. The details of the transformations can be found in the script. Then, it is saved in a geojson file, similar to the script above where we process the raw file with the coffee farms. This file will be later used for the development of the dashboard.

Next, a dataset for the RADD alerts is loaded (data/input/raw/10N_080W.tif). This needs more extensive transformation, as the type is of raster data. A raster data type is made up of pixels or cells and each pixel has an associated value. A grid of (usually square) pixels make up a raster image with the purpose of displaying a detailed image (a map, in our case). With the use of an affine transformation, the image coordinates (rows and columns) are mapped to the world geographic (x,y) coordinates. Since the raw file is a high-resolution image, only a window of the data is read, based on the bounds of the coffee farms plots. Within this window, we isolate the polygons that for which there has been an alert and collect it to a geojson FeatureCollection. This is finally saved in a geojson format, similar to the other cases. The produced file is then enriched with some necessary information, such as the year of the alert and the confidence level of the alert, before it is saved again. This file will also be later used for the development of the dashboard.

To run the script at once:
1. Follow steps 1,2,3 as listed above, if you haven't done already
2. Type scripts\read_open_source_data.py
You should be able to find two files titled in the folder path data\input\processed, titled 'amaz_gdf.geojson' & 'radd_gdf.geojson'.

3. 'find_intersection_and_save.py' needs to run last. This script loads the three processed geojson files and combines the datasets with the alerts into one, specifying the source of each row. Then, making use of a readily available geopandas function (sjoin), it looks for intersections between the coffee plots and the two alerts datasets. The function merges data from one set of geographical features with another set based on their locations and spatial interaction. It is not computationally expensive because of the way it operates. When it is required, Geopandas creates indices that represent the bounding boxes of the geometries (bounding boxes are the minima and maxima of the x and y coordinates of each geometry). When those do not satisfy the spatial relationship in question, the particular geometries will not. This step significantly reduces the number of detailed geometric calculations needed. The spatial relationship checked here is the intersection which is the most general of all and is true when the boundaries and/or interiors of the two geometries intersect in any way. 

When an intersection is found to be satisfied, geopandas merges the correspoding rows from each dataset. Thus, the sjoin function returns a new geodataframe that includes combined data from both input frames for the pairs of geometries that meet the criteria. When no intersection is found, a dataframe with columns identifying the coffee plots (name, id) and the alerts ('Amazonian', 'RADD') specifying 'No intersection' is returned. In any case, the result is saved in a csv file that will be later used for the dashboard development.

To run the script at once:
1. Follow steps 1,2,3 as listed above, if you haven't done already
2. Type scripts\find_intersection_and_save.py
You should be able to find a file titled 'intersection.csv' in the folder path data\input\processed.




- Raw Data: Description of the expected raw data format and sources.
- Processing Scripts: Explanation of the scripts used to process raw data into GeoJSON files.
1. Script Overview: Brief description of each script.
2. Running the Scripts: How to run the scripts.
3. Output: Description of the processed output files.

# Streamlit application locally
- Accessing the Dashboard: How to start the app and access the dashboard in a web browser.
- Basic Navigation: Guide to navigating the dashboard and using its features.

# Streamlit application deployed
- Step-by-step on how to deploy in streamlit and what to expect

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
Returns True if the geometries share some but not all points in common and the intersection of their interiors has the same dimension as the geometries themselves. This implies that the geometries share some part of their areas.

