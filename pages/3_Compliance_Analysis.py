import os
import base64
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
from compliance_operations import add_compliance_result
from document_operations import get_documents_by_pointer
from pointer_operations import update_pointer
from langchain_openai import OpenAIEmbeddings
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from typing import List
import fitz
import time
from pathlib import Path

dotenv_path = "pages/.env"
load_dotenv(dotenv_path=dotenv_path, override=True)

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
load_dotenv()

st.set_page_config(page_title="Compliance Analysis", page_icon="📊")
st.title("📊 Compliance Analysis")

# Load OpenAI API Key
# api_key = os.getenv("OPENAI_API_KEY")
api_key = st.secrets["OPENAI_API_KEY"]
if not api_key:
    st.error("OpenAI API key not found in .env file.")
    st.stop()

# Initialize OpenAI Client
client = OpenAI(api_key=api_key)

# Initialize Embeddings and LLM
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=api_key)
llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key)

# FAISS Index Paths
FAISS_INDEX_PATHS = {
    "Arabic": Path("pages") / "faiss_indexes" / "2024" / "Arabic",
    "English": Path("pages") / "faiss_indexes" / "2024" / "English"
}

# Utility Functions
def encode_image(image_path):
    """Encode an image to Base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def convert_pdf_to_images(pdf_path, output_folder="temp_images"):
    """Convert a PDF into individual images (one per page)."""
    doc = fitz.open(pdf_path)
    image_paths = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=300)  # Adjust DPI for better resolution
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
    return image_paths


def extract_text_with_openai_vision(image_paths, client):
    """Extract text from images using OpenAI Vision."""
    extracted_texts = []
    for idx, image_path in enumerate(image_paths, start=1):
        try:
            base64_image = encode_image(image_path)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"Extract the text from this page (Page {idx}):",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                            },
                        ],
                    }
                ],
                max_tokens=1000,  # Adjust to handle longer text
            )
            extracted_texts.append(response.choices[0].message.content.strip())
        except Exception as e:
            st.error(f"Error processing page {idx}: {e}")
    return "\n".join(extracted_texts)


def process_documents_with_vision(documents, client):
    """Process uploaded documents using OpenAI Vision."""
    temp_dir = "temp_files"
    os.makedirs(temp_dir, exist_ok=True)

    combined_text = ""
    for doc in documents:
        try:
            # Handle PDFs
            if doc["document_name"].lower().endswith(".pdf"):
                pdf_path = os.path.join(temp_dir, doc["document_name"])
                with open(pdf_path, "wb") as f:
                    f.write(doc["document_data"])

                # Convert PDF to images
                image_paths = convert_pdf_to_images(pdf_path, output_folder=temp_dir)
                text = extract_text_with_openai_vision(image_paths, client)

            # Handle images
            elif doc["document_name"].lower().endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(temp_dir, doc["document_name"])
                with open(image_path, "wb") as f:
                    f.write(doc["document_data"])

                # Extract text directly from the image
                text = extract_text_with_openai_vision([image_path], client)

            else:
                raise ValueError(f"Unsupported file format: {doc['document_name']}")

            combined_text += f"\n{text}"
        except Exception as e:
            st.error(f"Error processing document {doc['document_name']}: {e}")

    return combined_text


@st.cache_resource
def load_vector_store(path: str):
    """Load FAISS vector store."""
    try:
        return FAISS.load_local(
            folder_path=path,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    except Exception as e:
        st.error(f"Failed to load vector store at {path}: {e}")
        return None


def retrieve_with_scores(query: str, retriever) -> List[dict]:
    """Retrieve documents and their similarity scores from the vector store."""
    results = retriever.vectorstore.similarity_search_with_score(query)
    if not results:
        st.warning("No relevant chunks retrieved. Ensure the document is correctly embedded.")
        return []
    return [{"content": doc.page_content, "score": score} for doc, score in results]


def filter_relevant_chunks(chunks: List[dict]) -> List[dict]:
    """Filter out irrelevant chunks based on content quality."""
    relevant_chunks = []
    for chunk in chunks:
        content = chunk.get("content", "").strip()
        if len(content.split()) >= 5 and sum(c.isalpha() for c in content) / len(content) > 0.5:
            relevant_chunks.append(chunk)
    return relevant_chunks


# Compliance Analysis Logic
if "compliance_pointer" in st.session_state:
    pointer = st.session_state.compliance_pointer

    st.subheader("📌 Pointer Information")
    with st.container():
        st.markdown(f"""
        <div style="padding: 15px; border: 1px solid #fff; border-radius: 8px; background-color: #2b2b2b;">
            <p><strong>Pointer Name:</strong> {pointer['name']}</p>
            <p><strong>Objective:</strong> {pointer['objective']}</p>
            <p><strong>Compliance Requirements:</strong> {pointer['compliance_requirements']}</p>
            <p><strong>Language:</strong> {pointer['language']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.subheader("🔍 Compliance Check")
    if st.button("Check Compliance"):
        start_time = time.time()  # Start the timer
        st.info("Compliance check started... Please wait.")

        documents = get_documents_by_pointer(pointer["_id"])
        if documents:
            # Extract text from documents using Vision
            text_data = process_documents_with_vision(documents, client)

            # Load vector store
            vector_store_path = FAISS_INDEX_PATHS.get(pointer["language"])
            if not vector_store_path or not os.path.exists(vector_store_path):
                st.error(f"Vector store directory for {pointer['language']} not found.")
                st.stop()

            vector_store = load_vector_store(vector_store_path)
            if not vector_store:
                st.stop()

            retriever = vector_store.as_retriever(search_kwargs={"k": 5})
            retrieved_chunks = retrieve_with_scores(text_data, retriever)
            filtered_chunks = filter_relevant_chunks(retrieved_chunks)

            formatted_chunks = "\n".join(
                [f"Score: {chunk['score']}\nContent: {chunk['content']}" for chunk in filtered_chunks]
            )

            # LLM Evaluation
            system_prompt_template = ChatPromptTemplate.from_template(
                """
                You are an AI Assistant tasked with evaluating compliance based on the provided information.

                **Input Details:**
                - **Compliance Requirements**: {compliance_requirements}
                - **Supporting Document Points**: {supporting_document_points}
                - **Retrieved Document Context**: {formatted_chunks}

                **Your Task:**
                1. **Supporting Document Points Verification**:
                   - Analyze the "Supporting Document Points" provided.
                   - Verify their alignment with the retrieved document context.
                   - Identify any gaps or missing information for each supporting point.

                2. **Compliance Requirements Verification**:
                   - Evaluate the provided "Compliance Requirements."
                   - Use the retrieved document context and supporting document points for this evaluation.
                   - Determine whether the compliance requirements are fully met, partially met, or not met.
                   - Highlight which requirements or sub-requirements are not satisfied, if applicable.

                3. **Provide a Compliance Status**:
                   - Based on your evaluation, assign one of the following compliance statuses:
                     - **Fully Compliant**: All supporting document points and compliance requirements are fully addressed.
                     - **Partially Compliant**: Some points or requirements are addressed, but others are incomplete or missing.
                     - **Not Compliant**: The provided documents fail to meet the supporting document points and compliance requirements.

                **Output Format**:
                - **Compliance Status**: [Fully Compliant / Partially Compliant / Not Compliant]
                - **Reasons for Compliance Status**:
                  - Provide detailed explanations for each compliance requirement and supporting document point.
                  - For each point or requirement not met, include a reason why it was not satisfied.
                  - Sub-requirement Analysis (if applicable):
                    - Sub-requirement A: [Met/Not Met] - Explanation
                    - Sub-requirement B: [Met/Not Met] - Explanation
                    - Sub-requirement C: [Met/Not Met] - Explanation
                """
            )
            chain = system_prompt_template | llm | StrOutputParser()

            try:
                llm_response = chain.invoke({
                    "compliance_requirements": pointer['compliance_requirements'],
                    "supporting_document_points": pointer.get('supporting_document_points', 'No supporting points provided.'),
                    "formatted_chunks": formatted_chunks
                }).strip()

                compliance_status = llm_response.split("\n")[0].split(":")[-1].strip()
                reasons_for_status = "\n".join(llm_response.split("\n")[1:]).strip()

                add_compliance_result(pointer["_id"], compliance_status, reasons_for_status)
                pointer["compliance_status"] = compliance_status
                update_pointer(pointer["_id"], pointer)

                end_time = time.time()  # End the timer
                elapsed_time = end_time - start_time  # Calculate elapsed time

                st.success(f"Compliance Status: {compliance_status}")
                st.write(f"Reasons: {reasons_for_status}")
                st.info(f"Compliance check completed in {elapsed_time:.2f} seconds.")

            except Exception as e:
                st.error(f"Error processing LLM response: {e}")

        else:
            st.warning("No documents found for this compliance pointer.")
