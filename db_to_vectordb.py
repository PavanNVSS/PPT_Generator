import qdrant_client
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance
import sqlite3

# Set up connection to Qdrant Cloud
client = qdrant_client.QdrantClient(
    url="https://12dca0ba-749f-4b79-b71a-8a7e36bbe007.us-west-2-0.aws.cloud.qdrant.io",
    api_key="ha6xk8yCA44Eg_2HyE9vsFjutkperpSD7MqJ25NV1jpM7RmWxdaCFg",
    timeout=300
)

model = SentenceTransformer('all-MiniLM-L6-v2')

# Delete existing collection if it exists
collection_name = "vector_db"
try:
    client.delete_collection(collection_name)
    print(f"Deleted existing collection: {collection_name}")
except Exception as e:
    print(f"Collection doesn't exist or couldn't be deleted: {str(e)}")

# Create new collection with correct vector size
vector_params = VectorParams(
    size=384,
    distance=Distance.COSINE
)

client.create_collection(
    collection_name=collection_name,
    vectors_config=vector_params
)
print(f"Created new collection: {collection_name}")

def generate_embedding(texts, original_ids, original_texts):
    """
    Generates embeddings and includes original text as metadata.
    """
    embeddings = model.encode(texts)
    data = [
        {
            "id": int(original_id),  # Using original ID from database
            "vector": embedding.tolist(),
            "payload": {  # Metadata including original text
                "text": original_text
            }
        }
        for original_id, embedding, original_text in zip(original_ids, embeddings, original_texts)
    ]
    return data

# Connect to the SQLite database
conn = sqlite3.connect('embeddings_psy.db')
cursor = conn.cursor()

# Fetch the data
cursor.execute("SELECT id, section_text FROM embeddings")
your_data = cursor.fetchall()

# Separate IDs and texts
original_ids = [item[0] for item in your_data]
texts = [item[1] for item in your_data]

# Generate embeddings with metadata
generated_embeddings = generate_embedding(texts, original_ids, texts)

# Split the data into smaller batches
batch_size = 100
for i in range(0, len(generated_embeddings), batch_size):
    batch = generated_embeddings[i:i + batch_size]
    try:
        client.upsert(
            collection_name=collection_name,
            points=batch,
            wait=True
        )
        print(f"Uploaded batch {i//batch_size + 1} of {len(generated_embeddings)//batch_size + 1}")
    except Exception as e:
        print(f"Error uploading batch {i//batch_size + 1}: {str(e)}")


conn.close()