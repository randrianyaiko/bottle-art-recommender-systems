import threading
import numpy as np
from datetime import datetime
from typing import Dict, List
from src.vectorstore.store import SparseClient
from dotenv import load_dotenv
import os

# ------------------- Initialization -------------------
load_dotenv()
store = SparseClient()
EMA_ALPHA = float(os.getenv("EMA_ALPHA", 0.5))

EVENT_WEIGHTS = {
    "VIEW": 1,
    "ADD_TO_CART": 2,
    "UPDATE_CART_QUANTITY": 1,
    "REMOVE_FROM_CART": 0,
    "ORDER": 5,
}

# Thread-safe locks per user
user_locks: Dict[str, threading.Lock] = {}


# ------------------- Helper Functions -------------------
def get_user_lock(user_id: str) -> threading.Lock:
    """Return a threading.Lock for a user, creating one if necessary."""
    if user_id not in user_locks:
        user_locks[user_id] = threading.Lock()
    return user_locks[user_id]


def apply_ema(old_value: float, weight: float) -> float:
    """Compute the EMA for a single product interaction."""
    return EMA_ALPHA * weight + (1 - EMA_ALPHA) * old_value


def update_user_vector(user_id: str, user_events: List[dict]) -> dict:
    """
    Update a single user's sparse vector with all their events.
    Returns a dict ready for bulk upsert.
    """
    lock = get_user_lock(user_id)
    with lock:
        # Retrieve existing vector
        user_point = store.get_point_by_id(point_id=user_id)
        if user_point and "indices" in user_point:
            indices = np.array(user_point["indices"], dtype=int)
            values = np.array(user_point["values"], dtype=float)
        else:
            indices = np.array([], dtype=int)
            values = np.array([], dtype=float)

        # Convert to dict for quick updates
        product_values = {int(pid): val for pid, val in zip(indices, values)}

        # Apply EMA for each product sequentially
        for e in user_events:
            pid = int(e["product_id"])
            weight = EVENT_WEIGHTS[e["activity_type"]]
            old_val = product_values.get(pid, 0.0)
            product_values[pid] = apply_ema(old_val, weight)

        # Prepare final indices and values
        return {
            "id": user_id,
            "indices": list(product_values.keys()),
            "values": list(product_values.values()),
            "payload": {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        }


# ------------------- Main Batch Event Handler -------------------
def event_handler(events: List[dict]):
    """
    Process a batch of events and update Qdrant sparse vectors.
    Each user is updated exactly once using bulk insert.
    """
    if not isinstance(events, list):
        raise ValueError("event_handler expects a list of event dicts.")

    # Filter valid events
    valid_events = [
        e for e in events
        if e.get("activity_type") in EVENT_WEIGHTS
        and e.get("user_id") and e.get("product_id")
    ]

    if not valid_events:
        print("[WARN] No valid events found.")
        return

    # Group events by user
    user_event_map: Dict[str, List[dict]] = {}
    for e in valid_events:
        user_event_map.setdefault(e["user_id"], []).append(e)

    # Update each user's vector in memory
    bulk_updates = [update_user_vector(user_id, events) for user_id, events in user_event_map.items()]

    # Bulk upsert to Qdrant
    if bulk_updates:
        store.insert_sparse_points_bulk(bulk_updates)
        print(f"[BULK UPSERT] {len(bulk_updates)} user vectors updated.")
    else:
        print("[WARN] No updates to upsert.")
