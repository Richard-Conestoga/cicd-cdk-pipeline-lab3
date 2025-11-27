import json
import os
from datetime import datetime

def handler(event, context):
    print("Event:", json.dumps(event))

    return {
    "statusCode": 200,
    "headers": {
        "Content-Type": "application/json"
    },
    "body": json.dumps({
        "message": "Hello from CDK Pipeline!",  # changed message
        "time": datetime.utcnow().isoformat() + "Z",
        "stage": os.getenv("STAGE", "dev"),
        "version": "v3"
    })
}

