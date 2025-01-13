import pymongo
import streamlit as st

@st.cache_resource
def get_database():
    """
    Establish a MongoDB connection based on Streamlit secrets.
    Supports both local and cloud (MongoDB Atlas) connections.
    """
    try:
        mongo_secrets = st.secrets["mongo"]

        # Determine the connection method: Cloud URI or Local
        if "cloud_uri" in mongo_secrets:
            # Connect using MongoDB Atlas cloud URI
            client = pymongo.MongoClient(mongo_secrets["cloud_uri"])
        else:
            # Connect using local host and port
            client = pymongo.MongoClient(
                host=mongo_secrets.get("host", "localhost"),
                port=int(mongo_secrets.get("port", 27017)),
                username=mongo_secrets.get("username"),
                password=mongo_secrets.get("password")
            )

        # Access and return the specified database
        return client[mongo_secrets["db_name"]]

    except Exception as e:
        st.error(f"Error connecting to the database: {e}")
        return None
