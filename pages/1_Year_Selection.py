import streamlit as st

st.set_page_config(page_title="Year Selection", page_icon="📅")

st.title("Year Selection")
st.write("Select a year to continue with the compliance setup.")

if "selected_year" not in st.session_state:
    st.session_state.selected_year = 2024

year = st.selectbox("Choose the compliance year:", [2024])

if st.button("Proceed"):
    st.session_state.selected_year = year  
    st.session_state.edit_pointer = {}  
    st.switch_page("pages/2_Pointer_Definition.py")
