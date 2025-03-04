from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()


class QdrantDB:
    def __init__(self):
        self.client = QdrantClient(
            host=os.getenv("QDRANT_HOST"), port=int(os.getenv("QDRANT_PORT"))
        )
        self.collection_name = os.getenv("COLLECTION_NAME")
        # Load the embedding model
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")

        # Create collection if it doesn't exist
        self.init_collection()

    def init_collection(self):
        """Initialize the collection if it doesn't exist"""
        collections = self.client.get_collections().collections
        if not any(c.name == self.collection_name for c in collections):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # Dimension size for all-MiniLM-L6-v2
                    distance=Distance.COSINE,
                ),
            )

    def get_embedding(self, text: str):
        """Convert text to embedding vector"""
        return self.encoder.encode(text).tolist()

    def add_document(self, id: int, title: str, content: str, category: str = None):
        """Add a document to the collection"""
        # Combine title and content for better semantic search
        text_to_embed = f"{title} {content}"
        vector = self.get_embedding(text_to_embed)

        payload = {"title": title, "content": content, "category": category}

        self.client.upsert(
            collection_name=self.collection_name,
            points=[PointStruct(id=id, vector=vector, payload=payload)],
        )
        return True

    def search_documents(self, text: str, limit: int = 5):
        """Search for similar documents"""
        query_vector = self.get_embedding(text)

        results = self.client.search(
            collection_name=self.collection_name, query_vector=query_vector, limit=limit
        )

        return [
            {
                "id": result.id,
                "title": result.payload["title"],
                "content": result.payload["content"],
                "category": result.payload.get("category"),
                "similarity": result.score,
            }
            for result in results
        ]

    def delete_document(self, id: int):
        """Delete a document by ID"""
        self.client.delete(collection_name=self.collection_name, points_selector=[id])
        return True

    def update_document(
        self, id: int, title: str = None, content: str = None, category: str = None
    ):
        """Update a document by ID"""
        # Get existing document
        results = self.client.scroll(
            collection_name=self.collection_name,
            filter={"must": [{"key": "id", "match": {"value": id}}]},
        )[0]

        if not results:
            return False

        existing = results[0]

        # Update fields
        new_title = title if title is not None else existing.payload["title"]
        new_content = content if content is not None else existing.payload["content"]
        new_category = (
            category if category is not None else existing.payload.get("category")
        )

        # Create new embedding
        text_to_embed = f"{new_title} {new_content}"
        new_vector = self.get_embedding(text_to_embed)

        # Update document
        self.add_document(id, new_title, new_content, new_category)
        return True
