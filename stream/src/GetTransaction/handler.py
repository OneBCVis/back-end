import json
import pymysql
import logging
import os
import boto3
import jsonschema


# RDS settings
rds_secret_arn = os.environ['RDS_SECRETARN']
rds_proxy_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']
region = os.environ['RDS_REGION']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

schema = {
    "type": "object",
    "properties": {
        "txn_hash": {
            "type": "string",
            "pattern": "^0x[a-f0-9]{24,128}$"
        }
    },
    "required": ["txn_hash"]
}


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    return get_data_from_rds(event)


def get_data_from_rds(event):
    try:
        jsonschema.validate(event["pathParameters"], schema)
        txn_hash = event["pathParameters"]["txn_hash"]

        client = boto3.client(
            service_name='secretsmanager', region_name=region)
        response = client.get_secret_value(SecretId=rds_secret_arn)
        secret = json.loads(response["SecretString"])
        user_name = secret["username"]
        password = secret["password"]

        # Connect to the database
        conn = pymysql.connect(host=rds_proxy_host, user=user_name,
                               passwd=password, db=db_name, connect_timeout=5)

        cursor = conn.cursor()

        logger.info("SUCCESS: Able to connect to RDS MySQL instance")

        query_get_transaction = """
            SELECT
                t.txn_hash,
                t.status,
                t.amount,
                t.type,
                t.nonce,
                t.fee,
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'sender_key',   JSON_UNQUOTE(sender_key),
                            'amount',       amount
                        )
                    )
                    FROM txn_sender
                    WHERE txn_hash = t.txn_hash
                ) AS senders,
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'receiver_key', JSON_UNQUOTE(receiver_key),
                            'amount',       amount
                        )
                    )
                    FROM txn_receiver
                    WHERE txn_hash = t.txn_hash
                ) AS receivers
            FROM
                transaction t
            WHERE
                t.txn_hash = %s"""
        cursor.execute(query_get_transaction, (txn_hash))
        result_transaction = cursor.fetchall()

        cursor.close()

        conn.close()

        if (len(result_transaction) == 0):
            logger.error(f"ERROR: Transaction hash {txn_hash} not found")
            response = {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Transaction hash not found"
                })
            }
        else:
            response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "txn_hash": result_transaction[0][0],
                    "status": result_transaction[0][1],
                    "amount": result_transaction[0][2],
                    "type": result_transaction[0][3],
                    "nonce": result_transaction[0][4],
                    "fee": result_transaction[0][5],
                    "senders": json.loads(result_transaction[0][6]),
                    "receivers": json.loads(result_transaction[0][7])
                })
            }

    except jsonschema.ValidationError as e:
        logger.error(f"ERROR: JSON Schema Error occurred: {e}")
        response = {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Invalid transaction hash"
            })
        }

    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    except Exception as e:
        logger.error(f"ERROR: Error occurred: {e}")
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    return response
