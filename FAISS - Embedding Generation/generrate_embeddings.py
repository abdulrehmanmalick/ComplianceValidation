import os
import faiss
import numpy as np
from uuid import uuid4
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Initialize the embedding model
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

def process_documents_for_year_and_language(year, language, doc_path):
    """
    Process documents for a specific year and language, adding them to the FAISS vector store.
    """
    # Define FAISS index for local persistence
    embedding_dimension = len(embeddings.embed_query("test"))
    index = faiss.IndexFlatL2(embedding_dimension)

    # Initialize FAISS vector store with an in-memory document store
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )

    # Use SemanticChunker with percentile-based threshold for chunking
    text_splitter = SemanticChunker(
        embeddings, 
        breakpoint_threshold_type="percentile"
    )

    # Load and process the document
    if doc_path.endswith(".pdf"):
        loader = PyPDFLoader(doc_path)
    else:
        print(f"Unsupported file format: {doc_path}")
        return

    # Load document content and apply semantic chunking
    documents = loader.load()
    chunks = text_splitter.create_documents([doc.page_content for doc in documents])

    # Add chunks to FAISS index and document store
    uuids = [str(uuid4()) for _ in range(len(chunks))]
    for i, chunk in enumerate(chunks):
        chunk.metadata["language"] = language  # Tag the chunk by language
        vector_store.add_documents(documents=[chunk], ids=[uuids[i]])

    # Define persistence directory
    persist_directory = f"./faiss_indexes/{year}/{language}/"
    os.makedirs(persist_directory, exist_ok=True)

    # Save FAISS index locally
    faiss.write_index(index, os.path.join(persist_directory, "faiss_index.bin"))
    print(f"Processed and stored embeddings for year {year} in {language}.")

# Usage example for both English and Arabic documents
year = 2024
process_documents_for_year_and_language(year, "English", "./docs/2024/document_en.pdf")
process_documents_for_year_and_language(year, "Arabic", "./docs/2024/document_ar.pdf")
