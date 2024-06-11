import streamlit as st

# Page config
st.set_page_config(
    page_title="Background information",
    layout='wide'
)


text = """
# Intro
This dashboard aims to aid in detecting whether certain coffee plots are near deforested areas.
This is achieved by visualising coffee farms in the department of Huila in Colombia along with geographies
that are detected to be at risk of deforestation. A tabular view is also offered to inform on overlaps 
between the coffee farms and the deforested areas.

# Alerts
The first alert dataset, RADD, is developed by Wageningen University and Research (WUR) 
and is a deforestation alert product that uses data from the European Space Agency’s Sentinel-1 satellites 
to detect forest disturbances in near-real-time. 
Here is a [link] https://data.globalforestwatch.org/datasets/gfw::deforestation-alerts-radd/about") to access more details on RADD alerts, including the dataset.

The second alert dataset, Amazonian Colombia, was derived from interpreting satellite images from the Landsat 5 (TM) and 7 (ETM+) programs.
The layer lists the changes that forests have undergone in 2020-2022. 
Here we have focused on retrieving the areas with forest in 2020 that do not report this coverage for 2022.
Here is a [link] https://hub.arcgis.com/datasets/9ec021a002c64222a9ea26b1f766fa40/about to access the dataset and further information.

# Functionality
The first page of this dashboard, visualizes a map with the coffee farms and the geographies with deforestation alerts.
On the left sidebar, the user can navigate to the different pages of the dashboard. Below, some filtering options for the RADD alerts are offered.
The user can select which geometries with RADD alerts should be visible on the map based on the year they were registered 
and the confidence level of the alert. 
Each disturbance alert is detected from a single observation in the latest image if the forest disturbance probability is above 85%. 
If the forest disturbance probability reaches 97.5% in subsequent imagery within a maximum 90-day period, alerts are then marked as "high confidence". 

The user can zoom-in and zoom-out of the map by using the button on the top left corner. 
On the right top corner, there is a toggle button which can be used to select which datasets will be visible on the map.

The second page includes a table in standard format.
This table allows for a straightforward and clear analysis of the overlaps between coffee plots, Amazonian deforested areas, and RADD alerts.
"""

st.markdown(text) # or st.text
#st.markdown("[Radd alerts] https://data.globalforestwatch.org/datasets/gfw::deforestation-alerts-radd/about")

