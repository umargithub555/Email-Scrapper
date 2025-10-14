import os
from pymongo import MongoClient
from dotenv import load_dotenv
import pymongo
import pandas as pd



load_dotenv() # reads .env
MONGODB_URI = os.getenv("MONGO_CONNECTION_URL")

if not MONGODB_URI:
     raise SystemExit("Set MONGO_CONNECTION_URL in .env")

# Define the database and collection names as strings
DATABASE_NAME = "emailScrapper"
COLLECTION_NAME = "domains" 

# This function is now simplified and correct
def get_db_collection():
    client = MongoClient(MONGODB_URI)
    print("✅ DB connection successful")
    db = client[DATABASE_NAME] # Use the string name here
    collection = db[COLLECTION_NAME] # and the string name here
    return collection



# collection = get_db_collection()




# domain_list = [doc["domain"] for doc in collection.find({}, {"_id": 0, "domain": 1})]
# print(domain_list)




# def fetch_all_domains():
#     domains_list = [doc['domain'] for doc in collection.find({},{"_id":0, "domain":1})]
#     return domains_list


# def fetch_based_on_status(status:str):
#         query = {'status':status}

#         domains = collection.find(query, {"_id": 0, "domain": 1, "status": 1})

#         # for doc in domains:
#         #     print(doc["domain"], "-", doc["status"])

#         return domains








# assumes your CSV has ONE column named 'domain'
# df = pd.read_csv("domains_part1.csv")

# # Create documents with default email + status
# docs = [{"domain": d, "email": None, "status": "pending"} for d in df["Domain"][:10]]


# # --- Insert all at once ---

# result = collection.insert_many(docs)
# print(f"✅ Inserted {len(result.inserted_ids)} documents")




# --- Single insert example ---
# doc = {"domain": "example.com", "added_by": "me", "tags": ["test"]}
# res = collection.insert_one(doc)
# print("Inserted single doc id:", res.inserted_id)

# # --- Quick verify: find_one / count ---
# print("One doc from collection:", collection.find_one())
# print("Total documents:", collection.count_documents({}))

# # --- Bulk insert (no batching, all at once) ---
# domains = [f"site{i}.com" for i in range(1, 5001)]  # simulating 5k domains
# docs = [{"domain": d} for d in domains]

# result = collection.insert_many(docs)
# print(f"✅ Inserted {len(result.inserted_ids)} documents in one go")
