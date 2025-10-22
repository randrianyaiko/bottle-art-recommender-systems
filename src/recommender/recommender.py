from typing import List, Dict
from src.vectorstore.store import SparseClient
from src.recommender.aggregator import InteractionAggregator


class SparseRecommender:
    """
    High-level recommender built on top of Qdrant Sparse Vectors.
    """

    def __init__(self, top_k_similar_users: int = 5, top_k_items: int = 10):
        self.client = SparseClient()
        self.top_k_similar_users = top_k_similar_users
        self.top_k_items = top_k_items
        self.aggregator = InteractionAggregator(mode="sum")

    def get_similar_users(self, user_id: str) -> List[Dict]:
        """Retrieve similar users from Qdrant."""
        return self.client.search_similar_by_id(point_id=user_id, top_k=self.top_k_similar_users)

    def get_user_interactions(self, user_id: str) -> List[int]:
        """Retrieve indices (items) the user has interacted with."""
        user_data = self.client.get_point_by_id(user_id)
        if not user_data:
            raise ValueError(f"User {user_id} not found in collection.")
        return user_data["indices"]

    def recommend(self, user_id: str):
        """
        Generate item recommendations for a user.
        """
        similar_users = self.get_similar_users(user_id)
        user_interacted = self.get_user_interactions(user_id)
        recommendations = self.aggregator.aggregate(
            similar_users=similar_users,
            exclude_indices=user_interacted,
            top_k=self.top_k_items
        )
        
        return recommendations
