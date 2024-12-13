import streamlit as st
from pointer_operations import get_all_pointers, delete_pointer
from document_operations import delete_documents_by_pointer, get_documents_by_pointer
import base64


st.set_page_config(page_title="View Pointers", page_icon="📄")

col1, col2 = st.columns([8, 1])
with col1:
    st.title("Saved Pointers")
with col2:
    if st.button("Add New", key="add_new_top"):
        st.session_state.selected_year = 2024  
        st.session_state.edit_pointer = {}     
        st.switch_page("pages/2_Pointer_Definition.py")  

st.markdown("""
    <style>
    /* Style for the action buttons */
    .stButton>button {
        width: 150px;
    }
    /* Style for the boxes containing objectives, compliance requirements, and supporting document points */
    .content-box {
        border: 1px solid #4682B4;  /* Soft blue border */
        padding: 15px;
        border-radius: 10px;  /* Rounded corners */
        margin-bottom: 20px;
        background-color: #2C2C2C;  /* Dark grey background */
        color: #FFFFFF;  /* White text */
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.2);  /* Subtle shadow */
        font-size: 14px;
        line-height: 1.6;
    }
    .content-box div {
        margin-bottom: 5px;
    }
    /* Compliance Status styling with dynamic colors */
    .compliance-status {
        font-size: 16px;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .compliant {
        color: #32CD32;  /* Green */
    }
    .partially-compliant {
        color: #FFD700;  /* Yellow */
    }
    .not-compliant {
        color: #FF4500;  /* Red */
    }
    .not-checked {
        color: #4682B4;  /* Soft Blue */
    }
    </style>
""", unsafe_allow_html=True)

def format_with_lines(text):
    lines = text.strip().split("\n")
    formatted_text = "".join(
        [f"<div>{line.strip()}</div>" for line in lines if line.strip()]
    )
    return formatted_text


pointer_list = get_all_pointers()

if pointer_list:
    for idx, pointer in enumerate(pointer_list):
        st.subheader(f"Pointer Name: {pointer['name']}")
        st.write(f"**Year:** {pointer.get('year', '2024')}")

        st.markdown("**Objective:**")
        st.markdown(f"""
            <div class="content-box">
                {format_with_lines(pointer['objective'])}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("**Compliance Requirements:**")
        st.markdown(f"""
            <div class="content-box">
                {format_with_lines(pointer['compliance_requirements'])}
            </div>
        """, unsafe_allow_html=True)

        st.markdown("**Supporting Document Points:**")
        supporting_points = pointer.get('supporting_document_points', "No supporting points defined.")
        if supporting_points.strip():
            st.markdown(f"""
                <div class="content-box">
                    {format_with_lines(supporting_points)}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.write("No supporting points defined.")

        st.markdown("**Uploaded Documents:**")
        uploaded_documents = get_documents_by_pointer(pointer["_id"])
        if uploaded_documents:
            document_list_items = "".join([
                f"<div><a href='data:application/octet-stream;base64,{base64.b64encode(doc['document_data']).decode()}' download='{doc['document_name']}' style='color: #1E90FF;'>{doc['document_name']}</a></div>"
                for doc in uploaded_documents
            ])
            st.markdown(f"<div class='content-box'>{document_list_items}</div>", unsafe_allow_html=True)
        else:
            st.write("No documents uploaded.")

        compliance_status = pointer.get('compliance_status', 'Not Checked')
        status_class = "not-checked"
        if compliance_status == "Fully Compliant":
            status_class = "compliant"
        elif compliance_status == "Partially Compliant":
            status_class = "partially-compliant"
        elif compliance_status == "Not Compliant":
            status_class = "not-compliant"

        
        st.markdown(f"""
            <div class="compliance-status {status_class}">
                Compliance Status: {compliance_status}
            </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Edit", key=f"edit_{idx}"):
                st.session_state.edit_pointer = pointer
                st.switch_page("pages/2_Pointer_Definition.py")
        with col2:
            if st.button("Check Compliance", key=f"check_compliance_{idx}"):
                st.session_state.compliance_pointer = pointer
                st.switch_page("pages/3_Compliance_Analysis.py")
        with col3:
            if st.button("Delete", key=f"delete_{idx}"):
                delete_pointer(pointer["_id"])
                delete_documents_by_pointer(pointer["_id"])
                st.success(f"Pointer '{pointer['name']}' and its documents were successfully deleted.")
                st.rerun()
else:
    st.write("No pointers saved. Use the 'Add New' button to create one.")
