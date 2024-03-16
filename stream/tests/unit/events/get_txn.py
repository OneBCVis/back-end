import json

mock_event = {
    "pathParameters": {"txn_hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74"},
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

mock_txn = {
    "txn_hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74"
}

mock_txn_body = {
    "txn_hash": "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
    "status": "PENDING",
    "amount": 4,
    "type": 3,
    "nonce": 4726,
    "fee": 1,
    "senders": json.dumps([{"sender_key": "0x1", "amount": 1}, {"sender_key": "0x2", "amount": 3}]),
    "receivers": json.dumps([{"receiver_key": "0x3", "amount": 2}, {"receiver_key": "0x4", "amount": 2}]),
}


def get_txn():
    return {
        "event": mock_event,
        "txn": mock_txn,
        "txn_body": mock_txn_body
    }
