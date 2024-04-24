import streamlit as st
import pandas as pd

App_title = "Amazonian Deforestation Overlap"
App_subtitle = "Source: Laboratorio SIG y SR - Instituto SINCHI"

def main():
    st.set_page_config(App_title)
    st.title(App_title)
    st.caption(App_subtitle)

    # LOADING DATA
    colombia = pd.read_csv(r"C:\Users\lueva\OneDrive\Documentos\EAE\Code\Progreso\colombian_amazonas.csv")
    
    status = ''
    if status:
        colombia = colombia[colombia["deforestac"] == status]

    st.write(colombia.shape)
    st.write(colombia.head())
    st.write(colombia.columns)
    st.write(pd.unique(colombia["deforestac"]))
    

# types = pd.unique(["deforestac"])

# for t in types:
#     mean_area = colombia[colombia["deforestac"] == t]["area_ha"].mean()
#     print(str(t) + " area size (ha): " + str(mean_area))
    
#     number_of_polygons = colombia[colombia["deforestac"] == t]["area_ha"].count()
#     print(str(t) + " has " + str(number_of_polygons) + " polygons")

# pd.DataFrame([colombia.groupby(["deforestac"])["area_ha"].count(), colombia.groupby(["deforestac"])["area_ha"].mean()]).T

# DISPLAY FILTERS AND MAP

# DISPLAY METRICS

if __name__ == "__main__":
    main()