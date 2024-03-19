mock_event = {
    "headers": {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Content-Length": "39",
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
            "39"
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
    "path": "/stats",
    "pathParameters": None,
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
        "path": "/stats/",
        "protocol": "HTTP/1.1",
        "requestId": "b343c611-575b-4ec2-b7ae-77c1dd74f73d",
        "requestTime": "23/Feb/2024:17:01:28 +0000",
        "requestTimeEpoch": 1708707688,
        "resourceId": "123456",
        "resourcePath": "/stats/",
        "stage": "Prod"
    },
    "resource": "/stats/",
    "stageVariables": None
}


def get_stats():
    return {
        "event": mock_event,
        "start_time": "2024-02-23 22:13:29",
        "end_time": "2024-02-23 21:13:29",
        "transaction_count": 357481,
        "block_count": 811,
        "total_tx_amount": 269700,
        "total_tx_fee": 4741,
        "txn_pool": 741,
        "miners": [
            [
                "0x7a250d5630b4cf539739df2c5dacb4c659f2488e",
                241
            ],
            [
                "0x7a250d5630b4cf539739df2c5dacb4c659f2488d",
                142
            ],
            [
                "0x7a250d5630b4cf539739df2c5dacb4c659f2488g",
                103
            ],
            [
                "0x7a250d5630b4cf539739df2c5dacb4c659f2488h",
                99
            ],
            [
                "0x7a250d5630b4cf539739df2c5dacb4c659f2488f",
                76
            ]
        ]
    }
