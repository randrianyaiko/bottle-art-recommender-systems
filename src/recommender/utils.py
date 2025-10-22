from typing import List, Tuple

def print_recommendations(recommendations: List[Tuple[int, float]]):
    """Nicely print recommendations."""
    print("\nTop Recommendations:")
    for rank, (idx, score) in enumerate(recommendations, start=1):
        print(f"{rank:2d}. Item {idx:<5} | Score: {score:.4f}")
