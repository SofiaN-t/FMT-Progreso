import streamlit as st
from pages import streamlit_vector_layers
from pages import streamlit_intersection_table


# ----- Page configs -----
st.set_page_config(
    page_title="Coffee farms - Colombia",
)

# Page navigation
page = st.sidebar.selectbox("Select a page", ["Map", "Table"])

if page == 'Map':
    st.title("Map")
    streamlit_vector_layers.load_all_vectors
    streamlit_vector_layers.plot_all_vectors
elif page == 'Table':
    st.title("Interesections with deforestation alerts")
    streamlit_intersection_table.write_table