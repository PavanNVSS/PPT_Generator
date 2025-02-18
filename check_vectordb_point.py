# Import required libraries
import qdrant_client

# Set up connection to Qdrant Cloud
client = qdrant_client.QdrantClient(
    url="https://12dca0ba-749f-4b79-b71a-8a7e36bbe007.us-west-2-0.aws.cloud.qdrant.io",
    api_key="ha6xk8yCA44Eg_2HyE9vsFjutkperpSD7MqJ25NV1jpM7RmWxdaCFg",
    timeout=300
)
# Retrieve a specific point by its ID
point = client.retrieve(
    collection_name="vector_db",
    ids=[1],
    with_vectors=True # List of point IDs to retrieve
)

# Check and print the result
if point:
    print(point)
else:
    print("No point found with the given ID.")
