# Compliance Validation System

Welcome to the Compliance Validation System! This application is designed to assist organizations in defining, managing, and validating compliance pointers using modern AI technologies, including FAISS, LangChain, and OpenAI GPT.

## Features
* Define Compliance Pointers: Add objectives, compliance requirements, and supporting document points.
* Upload Supporting Documents: Upload files like PDFs, images, and more to support compliance validation.
* Automated Compliance Analysis: Validate compliance using FAISS embeddings and OpenAI GPT, with outputs like Fully Compliant, Partially Compliant, or Not Compliant.
* Pointer Management: View, edit, delete, and reanalyze compliance pointers with ease.

## Technologies Used
* Python: Backend and logic implementation.
* Streamlit: Frontend UI for ease of use.
* MongoDB: Database for storing compliance pointers, documents, and results.
* FAISS: Semantic embedding and vector search.
* OpenAI GPT: AI-based compliance evaluation.

## Getting Started
1. Prerequisites
* Python 3.8 or higher
* MongoDB Community Edition
* MongoDB Compass (optional for GUI)
* OpenAI API Key

2. Installation
* Create a Virtual Environment
    -   python -m venv venv
    -   venv\Scripts\activate

* Install Dependencies
    -   pip install -r requirements.txt

* Configure Secrets
    1. Add your MongoDB credentials in **.streamlit/secrets.toml**
    -   host = "localhost"
    -   port = 27017
    -   db_name = "compliance_db"
    2. Add your OpenAI API Key in **.env**
    -   OPENAI_API_KEY="your-openai-api-key"

3. MongoDB Setup

    1. Install MongoDB
    -   Download MongoDB Community Edition from **https://www.mongodb.com/try/download/community**
    -   Follow the installer instructions to set up MongoDB.

    2. Install MongoDB Compass
    -   Download MongoDB Compass from **https://www.mongodb.com/products/tools/compass** for a GUI to manage your database.

    3. Create Database and Collections
    -   Open MongoDB Compass and connect to your instance **mongodb://localhost:27017**
    -   Create a database named **compliance_db**
    -   Add the following collections:
        -   pointers
        -   documents
        -   compliance_results

4. Run the Application
-   Start the Streamlit application with:
    -   streamlit run Landing_Page.py

    -   Access the application at **http://localhost:8501**


## Application Flow
* Landing Page: Navigate through the sidebar or start the compliance process.
* Year Selection: Choose the compliance year (default is 2024).
* Pointer Definition:
* Define objectives, compliance requirements, and supporting document points.
* Upload supporting documents.
* Compliance Analysis:
* Extract document text using OpenAI Vision.
* Analyze compliance using FAISS embeddings and OpenAI GPT.
* View compliance status and detailed explanations.
* View Pointers:
* Manage saved pointers and documents.
* Edit, delete, or reanalyze pointers.

## Database Schema

1. Pointers

        { 
            "_id": "ObjectId",  
            "name": "string",  
            "objective": "string",  
            "compliance_requirements": "string", 
            "supporting_document_points": "string",  
            "language": "string",  
            "year": "integer",  
            "compliance_status": "string"  
        }

2. Documents

        {
            "_id": "ObjectId",
            "pointer_id": "ObjectId",
            "document_name": "string",
            "document_data": "binary",
            "upload_date": "datetime"
        }

3. Compliance Results

        {
            "_id": "ObjectId",
            "pointer_id": "ObjectId",
            "compliance_status": "string",
            "details": "string",
            "checked_date": "datetime"
        }

## Key Files

-   **Landing_Page.py**: Start page of the application.   <br>
-   **1_Year_Selection.py**: Year selection page.
-   **2_Pointer_Definition.py**: Pointer definition and document upload.
-   **3_Compliance_Analysis.py**: Compliance analysis logic.
-   **4_View_Pointers.py**: View and manage pointers.