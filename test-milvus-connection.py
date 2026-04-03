#!/usr/bin/env python3
"""Test Milvus connection via milvus-api.local:19530"""

from pymilvus import connections, Collection, MilvusException, FieldSchema, CollectionSchema, DataType
from pymilvus import utility

def test_milvus_connection():
    """Test basic Milvus connectivity and operations"""

    # Connect to Milvus
    try:
        connections.connect(
            alias="default",
            host="milvus-api.local",
            port=19530
        )
        print("✓ Successfully connected to Milvus at milvus-api.local:19530")
    except Exception as e:
        print(f"✗ Failed to connect: {e}")
        return False

    # Check server version
    try:
        server_info = utility.get_server_version()
        print(f"✓ Milvus server version: {server_info}")
    except Exception as e:
        print(f"⚠ Could not retrieve server version: {e}")

    # Create test collections
    try:
        for i in range(3, 6):
            collection_name = f"test_collection_{i}"
            
            # Check if collection exists, drop if it does
            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
            
            # Define schema
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
                FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=128),
                FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=500)
            ]
            schema = CollectionSchema(fields=fields, description=f"Test collection {i}")
            
            # Create collection
            Collection(name=collection_name, schema=schema)
            print(f"✓ Created collection: {collection_name}")
    except Exception as e:
        print(f"✗ Failed to create collections: {e}")
        return False

    # List existing collections
    try:
        collections = utility.list_collections()
        print(f"✓ Collections in Milvus: {collections if collections else '(none)'}")
    except Exception as e:
        print(f"✗ Failed to list collections: {e}")
        return False

    # Disconnect
    connections.disconnect(alias="default")
    print("✓ Disconnected from Milvus")

    return True

if __name__ == "__main__":
    print("Testing Milvus connection...\n")
    success = test_milvus_connection()
    print(f"\n{'Connection test PASSED' if success else 'Connection test FAILED'}")
