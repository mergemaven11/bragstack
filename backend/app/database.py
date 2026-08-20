from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")

client = MongoClient(MONGO_URL)
db = client["bragstack"]

entries_collection = db["entries"]
users_collection = db["users"]
impact_receipts_collection = db["impact_receipts"]
packet_export_audit_collection = db["packet_export_audit"]
packet_shares_collection = db["packet_shares"]