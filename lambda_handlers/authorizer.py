import os
import jwt
from jwt import InvalidTokenError

def handler(event, context):
    """Lambda JWT Authorizer using PyJWT"""

    token = event.get("authorizationToken")
    secret = os.environ.get("JWT_SECRET", "mysecret")

    try:
        # Decode JWT and verify signature
        decoded = jwt.decode(token, secret, algorithms=["HS256"])

        # Extract user_id - prioritize 'user_id' claim, fall back to 'sub'
        user_id = decoded.get("user_id") or decoded.get("sub", "unknown")

        return {
            "principalId": user_id,
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": event.get("methodArn")
                }]
            },
            "context": {
                "user_id": user_id
            }
        }

    except InvalidTokenError:
        # Invalid, expired, or tampered token
        return {
            "principalId": "unauthorized",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [{
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": event.get("methodArn")
                }]
            }
        }