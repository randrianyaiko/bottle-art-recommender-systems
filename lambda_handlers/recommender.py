import json
import logging
import os
from src.recommender.recommender import SparseRecommender

# --- GLOBAL SETUP (runs only once per container, not per invocation) ---
# This reduces cold start cost if you can preload the model here.
# Expensive initialization should NOT happen inside the handler.
recommender = SparseRecommender()

# Configure structured logging (best practice for CloudWatch readability)
logger = logging.getLogger()
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def handler(event, context):
    """
    AWS Lambda entrypoint for recommendation API.
    Expects an event with a 'user_id' key.
    """

    logger.debug("Received event: %s", json.dumps(event))

    user_id = event.get("user_id")
    if not user_id:
        logger.warning("Missing 'user_id' in event payload.")
        return _response(400, {"error": "Missing 'user_id' in request"})

    try:
        # Call recommender
        recommended = recommender.recommend(user_id)
        logger.info("Generated recommendations for user_id=%s", user_id)

        return _response(200, {"recommended": recommended})

    except Exception as e:
        # Log full traceback for debugging
        logger.exception("Failed to generate recommendations for user_id=%s", user_id)
        return _response(500, {"error": "Internal server error"})


# --- Helper function for consistent responses ---
def _response(status_code: int, body: dict):
    """Formats HTTP responses consistently."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
