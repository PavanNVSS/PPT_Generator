# Import required libraries
import qdrant_client

client = qdrant_client.QdrantClient(
    url="https://12dca0ba-749f-4b79-b71a-8a7e36bbe007.us-west-2-0.aws.cloud.qdrant.io",
    api_key="ha6xk8yCA44Eg_2HyE9vsFjutkperpSD7MqJ25NV1jpM7RmWxdaCFg",
    timeout=300
)

# Define the collection name
collection_name = "vector_db"
# Explore the database content
print(f"Exploring content of collection: {collection_name}")

try:
    print("did this")
    # Start with the initial scroll
    scroll_result, next_page = client.scroll(
        collection_name=collection_name,
        limit=100  # Fetch 100 points at a time
    )
    print("and?")
    # Initialize a counter for total points
    total_points = 0

    while scroll_result:
        print("its here?")
        print(f"Batch retrieved: {len(scroll_result)}")
        total_points += len(scroll_result)

        # Process the points in the current batch
        for i, point in enumerate(scroll_result):
            if point is None:
                print("its  nothere?")

                print(f"Point {i + 1} is None.")
            else:
                print("its here also")
                print(point)
                print(f"Point {i + 1}: ID={point.id}, Payload={point.payload['text']},")  # Show first 5 vector elements

        print("so its not here")
        # Fetch the next batch using the continuation token
        if next_page:
            scroll_result, next_page = client.scroll(
                collection_name=collection_name,
                limit=100,
                offset=next_page
            )
        else:
            # No more points to fetch
            break

    print(f"Total points retrieved: {total_points}")

except Exception as e:
    print(f"Error while exploring the database: {e}")
