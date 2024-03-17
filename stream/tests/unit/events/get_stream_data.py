mock_event = {
    "queryStringParameters": {
        "start_time": "2024-02-23 20:25:10.748",
        "end_time": "2024-02-23 20:25:10.147"
    },
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Content-Length": "72",
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
            "72"
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
    "path": "/stream",
    "pathParameters": None,
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
        "path": "/stream/",
        "protocol": "HTTP/1.1",
        "requestId": "2cbe9cda-69d2-4af9-98b3-bba7443e9c53",
        "requestTime": "23/Feb/2024:14:50:45 +0000",
        "requestTimeEpoch": 1708699845,
        "resourceId": "123456",
        "resourcePath": "/stream/",
        "stage": "Prod"
    },
    "resource": "/stream/",
    "stageVariables": None
}

mock_txns = [
    (
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c74",
        "PENDING",
        1,
        2,
        1
    ),
    (
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c75",
        "APPROVED",
        2,
        1,
        1
    ),
    (
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c76",
        "APPROVED",
        0,
        3,
        2
    )
]

mock_blocks = [
    (
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c77",
        "0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c78",
        '["0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c75",'
        + '"0x97aaa6c1bc101abecd1ebb4e1a7c067a71b2c1e3f9ef304909af86e5e2f84c76"]',
        2, 3, 2, "2024-02-23 20:25:10.748"
    )
]


def get_stream_data():
    return {
        "event": mock_event,
        "txns": mock_txns,
        "blocks": mock_blocks
    }
