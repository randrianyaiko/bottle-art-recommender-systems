import os
import uuid
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as rest_models

class SparseClient:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        qdrant_url = os.getenv('QDRANT_URL')
        api_key = os.getenv('QDRANT_API_KEY')
        self.sparse_name = os.getenv('QDRANT_SPARSE_NAME', 'sparse')
        self.collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'sparse_collection')

        if not qdrant_url:
            raise ValueError("QDRANT_URL must be set in environment")

        # Initialize Qdrant client
        self.client = QdrantClient(url=qdrant_url, api_key=api_key)

        # Check or create collection
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                sparse_vectors_config={
                    self.sparse_name: models.SparseVectorParams(
                        index=models.SparseIndexParams(on_disk=False)
                    )
                }
            )
            print(f"Collection '{self.collection_name}' created")
        else:
            print(f"Collection '{self.collection_name}' already exists")

    # -----------------------------
    # Insert a single sparse point
    # -----------------------------
    def insert_sparse_point(
        self,
        indices: List[int],
        values: List[float],
        payload: Optional[Dict[str, Any]] = None,
        point_id: Optional[str] = None
    ) -> str:
        """Insert a single sparse vector point"""
        if len(indices) != len(values):
            raise ValueError("Indices and values must have the same length")

        point_id = point_id or str(uuid.uuid4())
        point = rest_models.PointStruct(
            id=point_id,
            vector={self.sparse_name: rest_models.SparseVector(indices=indices, values=values)},
            payload=payload
        )
        self.client.upsert(collection_name=self.collection_name, points=[point])
        return point_id

    # -----------------------------
    # Bulk insert sparse points
    # -----------------------------
    def insert_sparse_points_bulk(
        self,
        vectors: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Bulk insert sparse points.
        Each dict in `vectors` must have:
          - 'indices': List[int]
          - 'values': List[float]
          - optional 'payload': Dict
          - optional 'id': str
        """
        points = []
        point_ids = []

        for vec in vectors:
            indices = vec['indices']
            values = vec['values']
            payload = vec.get('payload')
            point_id = vec.get('id', str(uuid.uuid4()))
            point_ids.append(point_id)

            if len(indices) != len(values):
                raise ValueError("Indices and values must have the same length")

            points.append(
                rest_models.PointStruct(
                    id=point_id,
                    vector={self.sparse_name: rest_models.SparseVector(indices=indices, values=values)},
                    payload=payload
                )
            )

        self.client.upsert(collection_name=self.collection_name, points=points)
        return point_ids

    # -----------------------------
    # Get a point by its ID
    # -----------------------------
    def get_point_by_id(
        self,
        point_id: str,
        with_payload: bool = True,
        with_vector: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a point by its ID, including sparse vector content.

        Returns:
            dict with:
                - 'id'
                - 'payload'
                - 'sparse_vector': {'indices': [...], 'values': [...]}
        """
        try:
            point = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id],
                with_vectors=with_vector
            )

            return {
                "id": point[0].id,
                "indices": point[0].vector['sparse'].indices,
                "values": point[0].vector['sparse'].values
            }
        
        except Exception as e:
            print(f"Error retrieving point with ID {point_id}: {e}")
            return None

    # -----------------------------
    # Search similar points by a reference point ID
    # -----------------------------
    def search_similar_by_id(
        self,
        point_id: str,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for points similar to a given point ID.

        Returns only:
            - 'id'
            - 'payload' (optional)
        """
        response = self.client.query_points(
            collection_name=self.collection_name,
            using=self.sparse_name,
            query=point_id,
            limit=top_k,
            with_vectors=True
        )

        results = []
        for hit in response.points:
            results.append({
                "id": hit.id,
                "payload": hit.payload,
                "indices": hit.vector['sparse'].indices,
                "values": hit.vector['sparse'].values
            })
        return results
