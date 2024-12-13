import streamlit as st

st.set_page_config(page_title="Compliance Validation System", page_icon="📄")

st.sidebar.title("Navigation")
st.sidebar.markdown("Use the sidebar to navigate between sections.")

st.title("Compliance Validation System")
st.write("Welcome to the Compliance Validation System. Use the navigation menu to start the compliance process.")

if st.button("Start Compliance Process"):
    st.session_state.edit_pointer = None  
    st.switch_page("pages/1_Year_Selection.py")  
