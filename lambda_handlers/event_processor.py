import json
import logging
from typing import List, Dict
from src.event_processor.processor import event_handler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    """
    AWS Lambda handler triggered by SQS (SNS → SQS subscription).
    Processes a batch of messages and sends them to the event_handler.
    
    Event structure:
    {
        "Records": [
            {
                "messageId": "...",
                "body": "{...}",  # SNS JSON payload
                ...
            },
            ...
        ]
    }
    """
    if "Records" not in event:
        logger.warning("No Records found in event")
        return {"status": "no_records"}

    parsed_events: List[Dict] = []

    for record in event["Records"]:
        try:
            # SQS body contains SNS JSON
            sns_message = json.loads(record["body"])
            
            # SNS message contains the actual user activity
            message_content = json.loads(sns_message["Message"])
            
            # Only keep relevant fields for event_handler
            parsed_event = {
                "activity_id": message_content.get("activity_id"),
                "user_id": message_content.get("user_id"),
                "activity_type": message_content.get("activity_type"),
                "product_id": str(message_content.get("product_id")),  # Ensure string
                "details": message_content.get("details"),
                "created_at": message_content.get("created_at")
            }
            parsed_events.append(parsed_event)
        except Exception as e:
            logger.error(f"Failed to parse record {record.get('messageId')}: {e}")

    if parsed_events:
        try:
            event_handler(parsed_events)
            logger.info(f"Processed {len(parsed_events)} events")
        except Exception as e:
            logger.error(f"Error processing events: {e}")
            # Optional: raise to trigger Lambda retry / DLQ
            raise e
    else:
        logger.warning("No valid events to process")
    return {"status": "success", "processed": len(parsed_events)}
