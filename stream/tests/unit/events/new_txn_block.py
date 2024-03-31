import base64
import json


mock_transaction_1 = {
    "Hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
    "Sender": [["0xF475fDC8633D4eF7FB7F82E93424Decc81e20485", 1], ["0xF475fDC8633D4eF7FB7F82E93424De892549635866", 2]],
    "Receiver": [["0xBA12222222228d8Ba445958a75a0704d566BF274", 2], ["0xBA12222222228d8Ba445958a75a026658658536988", 1]],
    "Amount": 3,
    "Status": "PENDING",
    "Type": 1,
    "Nonce": 1,
    "Fee": 1
}

mock_transaction_2 = {
    "Hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96",
    "Sender": [["0xF475fDC8633D4eF7FB7F82E93424Decc81e20471", 1]],
    "Receiver": [["0xBA12222222228d8Ba445958a75a0704d566BF263", 1]],
    "Amount": 1,
    "Status": "PENDING",
    "Type": 3,
    "Nonce": 2,
    "Fee": 1
}

mock_unpublished_transaction = {
    "Hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9e5454876564994848418448",
    "Sender": [["0xF475fDC8633D4eF7FB7F82E93424484514151489", 2]],
    "Receiver": [["0xBA12222222228d8Ba445958a75a0716992784785", 2]],
    "Amount": 2,
    "Status": "APPROVED",
    "Type": 2,
    "Nonce": 3,
    "Fee": 1
}

mock_block_1 = {
    "Hash": "0xcd7e18b71827fb389cb01cafcc8711ddaa0f5eccfbaebce7b6bfe69d4cf1419e",
    "PreviousBlockHash":
    "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f8e8d2a43",
    "Nonce": 1,
    "Difficulty": 1,
    "Height": 1,
    "Miner": "0x665d8a50912FC42A88233e9eA53e70980dcb9Ecd",
    "Timestamp": "Feb-18-2024 03:56:47 AM +UTC",
    "Transactions": [
        mock_transaction_1.copy(),
        mock_transaction_2.copy(),
        mock_unpublished_transaction
    ],
    "Uncles": [
        "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f8e874856",
        "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f74125896"
    ],
    "Sidecar": [
        {
            "ID": "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c4803894599629",
            "TransactionID": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96",
            "Size": 1024
        },
        {
            "ID": "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c4803895742157",
            "TransactionID": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96",
            "Size": 2048
        }
    ]
}

mock_block_1["Transactions"][0]['Status'] = "APPROVED"
mock_block_1["Transactions"][1]['Status'] = "APPROVED"

mock_event = {
    "Records": [
        {
            "kinesis": {
                "partitionKey": "partitionKey-03",
                "kinesisSchemaVersion": "1.0",
                "data": base64.b64encode(json.dumps({
                    "type": "TRANSACTION",
                    "data": mock_transaction_1
                }).encode()),
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
                "data": base64.b64encode(json.dumps({
                    "type": "TRANSACTION",
                    "data": mock_transaction_2
                }).encode()),
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
                "data": base64.b64encode(json.dumps({
                    "type": "TRANSACTION",
                    "data": mock_transaction_1
                }).encode()),
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
                "data": base64.b64encode(json.dumps({
                    "type": "BLOCK",
                    "data": mock_block_1
                }).encode()),
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


def get_new_txn_block():
    return {
        "event": mock_event,
        "transaction_1": mock_transaction_1,
        "transaction_2": mock_transaction_2,
        "duplicate_transaction": mock_transaction_1,
        "unpublished_transaction": mock_unpublished_transaction,
        "block_1": mock_block_1
    }
