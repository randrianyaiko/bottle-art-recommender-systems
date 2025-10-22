from collections import defaultdict
from typing import List, Dict


class InteractionAggregator:
    """
    Aggregates item interaction scores from multiple similar users.
    """

    def __init__(self, mode: str = "sum") -> None:
        """
        Args:
            mode (str): 'sum' or 'average' — defines how to combine similar users' scores.
        """
        if mode not in {"sum", "average"}:
            raise ValueError("mode must be 'sum' or 'average'")
        self.mode = mode

    def aggregate(
        self,
        similar_users: List[Dict[str, List[float]]],
        exclude_indices: List[int],
        top_k: int = 10
    ) -> List[int]:
        """
        Combine sparse vectors from similar users into item recommendations.

        Args:
            similar_users: List of dicts with 'indices' and 'values'
            exclude_indices: Items the target user already interacted with
            top_k: Number of top items to return

        Returns:
            Sorted list of item indices (highest score first)
        """
        # Step 1: Aggregate contributions
        score_map: Dict[int, List[float]] = defaultdict(list)
        for user in similar_users:
            for idx, val in zip(user.get("indices", []), user.get("values", [])):
                score_map[idx].append(val)

        # Step 2: Compute final scores per item
        aggregated_scores: Dict[int, float] = {}
        for idx, vals in score_map.items():
            if idx in exclude_indices:
                continue
            aggregated_scores[idx] = (
                sum(vals) / len(vals) if self.mode == "average" else sum(vals)
            )

        # Step 3: Sort by score (descending) and return only the item indices
        sorted_indices = [
            idx for idx, _ in sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)
        ]
        return sorted_indices[:top_k]
