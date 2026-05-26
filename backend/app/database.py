import os

from pymongo import MongoClient


MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_URL)

db = client["bragstack"]
entries_collection = db["entries"]