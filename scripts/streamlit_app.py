import streamlit as st
import pandas as pd

App_title = "Amazonian Deforestation Overlap"
App_subtitle = "Source: Laboratorio SIG y SR - Instituto SINCHI"

def main():
    st.set_page_config(App_title)
    st.title(App_title)
    st.caption(App_subtitle)

    # LOADING DATA
    Colombia = pd.read_csv(r"C:\Users\lueva\OneDrive\Documentos\EAE\Code\Progreso\Colombian_amazonas.csv")
    
    Status = "Perdida"
    Colombia = Colombia[Colombia["deforestac"] == Status]

    st.write(Colombia.shape)
    st.write(Colombia.head())
    st.write(Colombia.columns)

    # DISPLAY FILTERS AND MAP

    # DISPLAY METRICS




if __name__ == "__main__":
    main()