import os
import pymongo
import google.generativeai as genai
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# MongoDB setup
client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["ashtavakra"]
collection = db["verses"]

# Gemini setup
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("📦 DB Name:", db.name)
print("📂 Collection Name:", collection.name)
print("📊 Total documents in collection:", collection.count_documents({}))

# Load documents without embeddings
documents = list(collection.find({"embedding": {"$exists": False}}))

print(f"📄 Found {len(documents)} documents to embed.")

for doc in tqdm(documents, desc="🔗 Generating embeddings"):
    try:
        # Combine fields into one meaningful text
        text_to_embed = f"{doc.get('sanskrit', '')}\n{doc.get('transliteration', '')}\n{doc.get('english', '')}\n{doc.get('commentary', '')}"

        # Call Gemini embedding API
        response = genai.embed_content(
            model="models/embedding-001",
            content=text_to_embed,
            task_type="retrieval_document",  # ✅ fixed: lowercase
            title="Ashtavakra Gita Verse"    # ✅ required for document embeddings
        )

        # Save embedding in the document
        embedding = response["embedding"]
        collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"embedding": embedding}}
        )

    except Exception as e:
        print(f"❌ Failed on {doc['_id']}: {e}")

print("✅ Embedding generation completed.")
