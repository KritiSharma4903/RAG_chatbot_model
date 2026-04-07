from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
client = MongoClient(MONGODB_URL)
db = client["invoice_ai_db"]

invoice_collection = db["invoices"]

print("Connected Successfully")

# Test Insert
test_data = {
    "invoice_number": "INV001",
    "vendor_name": "ABC Company",
    "total_amount": 5000
}

result = invoice_collection.insert_one(test_data)

print("Inserted ID:", result.inserted_id)

