import os
import pymongo
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["ashtavakra"]
collection = db["verses"]

# Load Local Model
print("📥 Loading Local Embedding Model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("📦 DB Name:", db.name)
print("📂 Collection Name:", collection.name)
print("📊 Total documents in collection:", collection.count_documents({}))

# Load ALL documents (Force regenerate for new model)
documents = list(collection.find({}))

print(f"📄 Found {len(documents)} documents to embed.")

for doc in tqdm(documents, desc="🔗 Generating local embeddings"):
    try:
        # Combine fields
        text_to_embed = f"{doc.get('sanskrit', '')}\n{doc.get('transliteration', '')}\n{doc.get('english', '')}\n{doc.get('commentary', '')}"

        # Generate Embedding (Locally!)
        embedding = model.encode(text_to_embed).tolist()

        # Save embedding
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": embedding}}
        )

    except Exception as e:
        print(f"❌ Failed on {doc['_id']}: {e}")

print("✅ Local Embedding generation completed.")
