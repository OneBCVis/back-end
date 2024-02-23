mock_event = {
    "Records": [
        {
            "kinesis": {
                "partitionKey": "partitionKey-03",
                "kinesisSchemaVersion": "1.0",
                "data": "eyJ0eXBlIjogIlRSQU5TQUNUSU9OIiwgImRhdGEiOiB7ICJIYXNoIjoiMHg5N2FhYTZjMWJjMTAxYWJlY2QxZWJiNGUxYTdjMDY3YTcxYjJjMWUzZjllZjMwNDkwOWFmODZlNWUyZjg0Yzc0IiwgIlNlbmRlciI6WyIweEY0NzVmREM4NjMzRDRlRjdGQjdGODJFOTM0MjREZWNjODFlMjA0ODUiXSwgIlJlY2VpdmVyIjpbIjB4QkExMjIyMjIyMjIyOGQ4QmE0NDU5NThhNzVhMDcwNGQ1NjZCRjI3NCJdLCAiQW1vdW50IjoxLCAiU3RhdHVzIjoiUEVORElORyIgfX0=",
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
        },
        {
            "kinesis": {
                "partitionKey": "partitionKey-03",
                "kinesisSchemaVersion": "1.0",
                "data": "eyJ0eXBlIjogIlRSQU5TQUNUSU9OIiwgImRhdGEiOiB7ICJIYXNoIjoiMHg5N2FhYTZjMWJjMTAxYWJlY2QxZWJiNGUxYTdjMDY3YTcxYjJjMWUzZjllZjMwNDkwOWFmODZlNWUyZjg0Yzk2IiwgIlNlbmRlciI6WyIweEY0NzVmREM4NjMzRDRlRjdGQjdGODJFOTM0MjREZWNjODFlMjA0NzEiXSwgIlJlY2VpdmVyIjpbIjB4QkExMjIyMjIyMjIyOGQ4QmE0NDU5NThhNzVhMDcwNGQ1NjZCRjI2MyJdLCAiQW1vdW50IjoyLCAiU3RhdHVzIjoiUEVORElORyIgfX0=",
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
        },
        {
            "kinesis": {
                "partitionKey": "partitionKey-03",
                "kinesisSchemaVersion": "1.0",
                "data": "eyJ0eXBlIjogIkJMT0NLIiwgImRhdGEiOiB7ICJIYXNoIjoiMHhjZDdlMThiNzE4MjdmYjM4OWNiMDFjYWZjYzg3MTFkZGFhMGY1ZWNjZmJhZWJjZTdiNmJmZTY5ZDRjZjE0MTllIiwgIlByZXZpb3VzQmxvY2tIYXNoIjoiMHg3NzliODI4NzNjNTVhZjAzMzU5ZDNmMzNmNTBhNmYwNjYyNTJjY2NhZjVkOWQzYzQ5NmQ4NTk3ZjhlOGQyYTQzIiwgIlRpbWVzdGFtcCI6IkZlYi0xOC0yMDI0IDAzOjU2OjQ3IEFNICtVVEMiLCAiTWluZXIiOiIweDY2NWQ4YTUwOTEyRkM0MkE4ODIzM2U5ZUE1M2U3MDk4MGRjYjlFY2QiLCAiVHJhbnNhY3Rpb25zIjpbIjB4OTdhYWE2YzFiYzEwMWFiZWNkMWViYjRlMWE3YzA2N2E3MWIyYzFlM2Y5ZWYzMDQ5MDlhZjg2ZTVlMmY4NGM3NCIsICIweDk3YWFhNmMxYmMxMDFhYmVjZDFlYmI0ZTFhN2MwNjdhNzFiMmMxZTNmOWVmMzA0OTA5YWY4NmU1ZTJmODRjOTYiXSB9fQ==",
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
        }
    ]
}

mock_transaction_1 = {
    "Hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
    "Sender": ["0xF475fDC8633D4eF7FB7F82E93424Decc81e20485"],
    "Receiver": ["0xBA12222222228d8Ba445958a75a0704d566BF274"],
    "Amount": 1,
    "Status": "PENDING"
}

mock_transaction_2 = {
    "Hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96",
    "Sender": ["0xF475fDC8633D4eF7FB7F82E93424Decc81e20471"],
    "Receiver": ["0xBA12222222228d8Ba445958a75a0704d566BF263"],
    "Amount": 2,
    "Status": "PENDING"
}

mock_block_1 = {
    "Hash": "0xcd7e18b71827fb389cb01cafcc8711ddaa0f5eccfbaebce7b6bfe69d4cf1419e",
    "PreviousBlockHash":
    "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f8e8d2a43",
    "Timestamp": "Feb-18-2024 03:56:47 AM +UTC",
    "Miner": "0x665d8a50912FC42A88233e9eA53e70980dcb9Ecd",
    "Transactions": [
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96"
    ]
}


def get_new_txn_block():
    return {
        "event": mock_event,
        "transaction_1": mock_transaction_1,
        "transaction_2": mock_transaction_2,
        "block_1": mock_block_1
    }
