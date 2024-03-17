import json


mock_block = {
    "block_hash": "0xcd7e18b71827fb389cb01cafcc8711ddaa0f5eccfbaebce7b6bfe69d4cf1419e",
    "previous_block_hash":
    "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f8e8d2a43",
    "nonce": 1,
    "difficulty": 1,
    "height": 1,
    "miner": "0x665d8a50912FC42A88233e9eA53e70980dcb9Ecd",
    "time_stamp": "Feb-18-2024 03:56:47 AM +UTC",
    "transactions": [
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c96",
    ],
    "uncles": [
        "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f8e874856",
        "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c496d8597f74125896",
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9e5454876564994848418448"
    ],
    "sidecar": [
        {
            "ID": "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c4803894599629",
            "Size": 1024
        },
        {
            "ID": "0x779b82873c55af03359d3f33f50a6f066252cccaf5d9d3c4803895742157",
            "Size": 2048
        }
    ],
    "total_amount": 100,
    "total_fee": 10,
    "txn_count": 2
}

mock_event = {
    "pathParameters": {
        "block_hash": mock_block["block_hash"]
    },
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Content-Length": "82",
        "Host": "localhost:3000",
        "User-Agent": "python-requests/2.31.0",
        "X-Forwarded-Port": "3000",
        "X-Forwarded-Proto": "http"
    },
    "httpMethod": "GET",
    "isBase64Encoded": False,
    "multiValueHeaders": {
        "Accept": [
            "*/*"
        ],
        "Accept-Encoding": [
            "gzip, deflate"
        ],
        "Connection": [
            "keep-alive"
        ],
        "Content-Length": [
            "82"
        ],
        "Host": [
            "localhost:3000"
        ],
        "User-Agent": [
            "python-requests/2.31.0"
        ],
        "X-Forwarded-Port": [
            "3000"
        ],
        "X-Forwarded-Proto": [
            "http"
        ]
    },
    "multiValueQueryStringParameters": None,
    "path": "/transaction",
    "queryStringParameters": None,
    "requestContext": {
        "accountId": "123456789012",
        "apiId": "1234567890",
        "domainName": "localhost:3000",
        "extendedRequestId": None,
        "httpMethod": "GET",
        "identity": {
            "accountId": None,
            "apiKey": None,
            "caller": None,
            "cognitoAuthenticationProvider": None,
            "cognitoAuthenticationType": None,
            "cognitoIdentityPoolId": None,
            "sourceIp": "127.0.0.1",
            "user": None,
            "userAgent": "Custom User Agent String",
            "userArn": None
        },
        "path": "/transaction/",
        "protocol": "HTTP/1.1",
        "requestId": "fb33dd6d-b06b-495f-a03e-ff1e718553a9",
        "requestTime": "23/Feb/2024:13:31:11 +0000",
        "requestTimeEpoch": 1708695071,
        "resourceId": "123456",
        "resourcePath": "/transaction/",
        "stage": "Prod"
    },
    "resource": "/transaction/",
    "stageVariables": None
}


def get_block():
    return {
        "event": mock_event,
        "block": mock_block
    }
