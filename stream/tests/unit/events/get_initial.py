import json

mock_event = {
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
    "path": "/initial/",
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

mock_data = {
    "txn_types": [
        {
            "type": 0,
            "name": "Legacy"
        },
        {
            "type": 1,
            "name": "Transfer"
        },
        {
            "type": 2,
            "name": "Contract Creation"
        },
        {
            "type": 3,
            "name": "Contract Execution"
        },
        {
            "type": 4,
            "name": "Shared Blob"
        }
    ],
    "txn_pool": 4785
}


def get_initial():
    return {
        "event": mock_event,
        "data": mock_data
    }
