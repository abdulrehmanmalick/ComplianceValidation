import streamlit as st
from pointer_operations import add_pointer, update_pointer
from document_operations import add_document, get_documents_by_pointer, delete_document
from bson.objectid import ObjectId
import regex as re

st.set_page_config(page_title="Pointer Definition", page_icon="📝")

if st.session_state.get("edit_pointer") and st.session_state.edit_pointer != {}:
    st.title("Edit Pointer")
    pointer_data = st.session_state.edit_pointer
    edit_mode = True
else:
    st.title("Define Pointer for Compliance")
    pointer_data = {
        "name": "",
        "objective": "",
        "compliance_requirements": "",
        "supporting_document_points": "",  
        "language": "English",
        "uploaded_files": None,
        "compliance_status": "Not Checked",
        "year": st.session_state.get("selected_year", "2024")
    }
    edit_mode = False

def remove_existing_numbers(text):
    lines = text.strip().split("\n")
    cleaned_text = "\n".join([re.sub(r"^\d+\.\s*", "", line.strip()) for line in lines if line.strip()])
    return cleaned_text

pointer_name = st.text_input("Pointer Name", value=pointer_data.get("name", ""))
objective = st.text_area("Objective", value=remove_existing_numbers(pointer_data.get("objective", "")))
compliance_requirements = st.text_area("Compliance Requirements", value=remove_existing_numbers(pointer_data.get("compliance_requirements", "")))

supporting_document_points = st.text_area(
    "Supporting Document Points",
    value=remove_existing_numbers(pointer_data.get("supporting_document_points", ""))
)

language = st.selectbox("Select Language for Compliance", ["English", "Arabic"], index=0 if pointer_data.get("language", "English") == "English" else 1)

st.header("Upload Supporting Documents")
uploaded_files = st.file_uploader("Upload files", type=["pdf", "docx", "ppt", "jpeg", "png", "pptx"], accept_multiple_files=True)

if edit_mode:
    st.subheader("Existing Uploaded Documents")
    existing_documents = get_documents_by_pointer(pointer_data["_id"])
    if existing_documents:
        for doc in existing_documents:
            doc_name = doc["document_name"]
            col1, col2 = st.columns([8, 1])
            with col1:
                if doc_name.lower().endswith(('.png', '.jpeg', '.jpg')):
                    st.image(doc["document_data"], caption=doc_name, use_column_width=True)
                else:
                    st.write(f"[{doc_name}](#)")  # Adjust for download link if needed
            with col2:
                delete_button = st.button("🗑️", key=f"delete_{doc['_id']}")
                if delete_button:
                    delete_document(doc["_id"])
                    st.success(f"Document deleted successfully.")
                    
                    # Update the query parameters to reload the page
                    st.query_params.clear()
    else:
        st.write("No previously uploaded documents.")

if st.button("Save Pointer"):
    pointer_data["name"] = pointer_name
    pointer_data["objective"] = remove_existing_numbers(objective)
    pointer_data["compliance_requirements"] = remove_existing_numbers(compliance_requirements)
    pointer_data["supporting_document_points"] = remove_existing_numbers(supporting_document_points)  # Save the new field
    pointer_data["language"] = language
    pointer_data["compliance_status"] = "Not Checked"
    pointer_data["year"] = pointer_data.get("year", st.session_state.get("selected_year", "2024"))

    if not edit_mode and not uploaded_files:
        st.warning("Please upload at least one supporting document before saving the pointer.")
    else:
        if edit_mode:
            update_pointer(pointer_data["_id"], pointer_data)
            st.success("Pointer updated successfully.")
            del st.session_state.edit_pointer 
        else:
            pointer_id = add_pointer(pointer_data)
            st.success(f"Pointer saved successfully with ID: {pointer_id}")
            pointer_data["_id"] = ObjectId(pointer_id)

        if uploaded_files:
            for uploaded_file in uploaded_files:
                add_document(pointer_data["_id"], uploaded_file.name, uploaded_file.getvalue())
                st.write(f"Uploaded document: {uploaded_file.name}")

        st.session_state.compliance_pointer = pointer_data

        # Redirect to the View Pointers page
        st.query_params.from_dict({"page": "View_Pointers"})
