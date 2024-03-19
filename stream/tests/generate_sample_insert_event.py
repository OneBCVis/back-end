import json
import base64
import random

from integration.generate_data import generate_random_block, generate_random_txn


records = []

for _ in range(100):
    type = random.randint(0, 20)
    test_event, partition_key = None, None
    if (type != 0):
        test_event, partition_key = generate_random_txn()
    else:
        test_event, partition_key = generate_random_block()
    records.append({
        "kinesis": {
            "partitionKey": "partitionKey-03",
            "kinesisSchemaVersion": "1.0",
            "data": str(base64.b64encode(json.dumps(test_event).encode()))[2:-1],
            "sequenceNumber": "49545115243490985018280067714973144582180062593244200961",
            "approximateArrivalTimestamp": 1428537600.0
        },
        "eventSource": "aws:kinesis",
        "eventID": "shardId-000000000000:49545115243490985018280067714973144582180062593244200961",
        "invokeIdentityArn": "arn:aws:iam::EXAMPLE",
        "eventVersion": "1.0",
        "eventName": "aws:kinesis:record",
        "eventSourceARN": "arn:aws:kinesis:EXAMPLE",
        "awsRegion": "us-east-1"
    })


with open('../test-data/sample_insert_event.json', 'w') as outfile:
    json.dump({"Records": records}, outfile, indent=2)
