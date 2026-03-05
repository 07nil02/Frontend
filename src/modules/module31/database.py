from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv()

def get_db():
    """
    Connects to the MongoDB database using URI from .env
    and returns the database object.
    """
    uri = os.getenv("MONGO_URI")

    client = MongoClient(uri)

    db = client["module31_db"]

    return db


if __name__ == '__main__':
    db = get_db()
    print("Successfully connected to the MongoDB database.")
    print("Collections:", db.list_collection_names())