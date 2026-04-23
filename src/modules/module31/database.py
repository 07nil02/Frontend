from pymongo import MongoClient
import os
import streamlit as st
import certifi

# Only use dotenv locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

def get_db():
    # Try Streamlit secrets first (Cloud)
    try:
        uri = st.secrets.get("MONGO_URI")
    except Exception:
        uri = None

    # Fallback to .env (local)
    if not uri:
        uri = os.getenv("MONGO_URI")

    if not uri:
        raise ValueError("MongoDB URI not found")

    client = MongoClient(
        uri,
        tls=True,
        tlsCAFile=certifi.where()
    )

    return client["module31_db"]

if __name__ == '__main__':
    db = get_db()
    print("Successfully connected to the MongoDB database.")
    print("Collections:", db.list_collection_names())