import pymongo
import streamlit as st

@st.cache_resource
def get_database():
    mongo_secrets = st.secrets["mongo"]
    if "username" in mongo_secrets and "password" in mongo_secrets:
        client = pymongo.MongoClient(
            host=mongo_secrets["host"],
            port=int(mongo_secrets["port"]),
            username=mongo_secrets["username"],
            password=mongo_secrets["password"]
        )
    else:
        client = pymongo.MongoClient(
            host=mongo_secrets["host"],
            port=int(mongo_secrets["port"])
        )
    return client[mongo_secrets["db_name"]]
