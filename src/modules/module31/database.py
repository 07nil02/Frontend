from pymongo import MongoClient
from dotenv import load_dotenv
import os
import streamlit as st

# Load variables from .env for local development
load_dotenv()

def get_db():
    """
    Connects to the MongoDB database using URI from st.secrets or .env
    and returns the database object.
    """
    # Streamlit throws FileNotFoundError if secrets.toml isn't found locally
    try:
        uri = st.secrets.get("MONGO_URI")
    except Exception:
        uri = None
        
    if not uri:
        uri = os.getenv("MONGO_URI")

    client = MongoClient(uri)

    db = client["module31_db"]

    return db


if __name__ == '__main__':
    db = get_db()
    print("Successfully connected to the MongoDB database.")
    print("Collections:", db.list_collection_names())