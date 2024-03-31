import json
import pymysql
from datetime import datetime
import logging
import os
import boto3
import jsonschema


# CORS
cors_origin = os.environ['CORS_ORIGIN']
headers = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": cors_origin,
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "GET"
}

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
        "start_time": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}$"
        },
        "end_time": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}.[0-9]{3}$"
        }
    },
    "required": ["start_time", "end_time"]
}


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    return get_data_from_rds(event)


def get_data_from_rds(event):
    try:
        params = event["queryStringParameters"]
        jsonschema.validate(params, schema)

        try:
            datetime.strptime(
                params["start_time"], '%Y-%m-%d %H:%M:%S.%f')
            datetime.strptime(
                params["end_time"], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError as e:
            logger.error(f"ERROR: Invalid date format: {e}")
            return {
                'statusCode': 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                'body': json.dumps('Invalid start_time or end_time format. Please use the format: YYYY-MM-DD HH:MM:SS.SSS')
            }

        start_timestamp = params["start_time"]
        end_timestamp = params["end_time"]

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

        query_get_transactions = """
            SELECT t.txn_hash, t.status, t.amount, t.type, t.fee
            FROM transaction t
            WHERE t.insert_time >= %s AND t.insert_time  < %s"""
        cursor.execute(query_get_transactions,
                       (start_timestamp, end_timestamp))
        result_transactions = cursor.fetchall()

        query_get_blocks = """
            SELECT
                b.block_hash,
                b.previous_block_hash,
                JSON_ARRAYAGG(bt.txn_hash) AS transactions,
                b.total_amount,
                b.total_fee,
                b.txn_count,
                b.time_stamp,
                b.miner
            FROM
                block b
            LEFT JOIN block_txn bt ON b.block_hash = bt.block_hash
            WHERE
                b.insert_time >= %s AND b.insert_time < %s
            GROUP BY
                b.block_hash"""
        cursor.execute(query_get_blocks, (start_timestamp, end_timestamp))
        result_blocks = cursor.fetchall()

        cursor.close()
        conn.close()

        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "transactions": get_transaction_response(result_transactions),
                "blocks": get_block_response(result_blocks)
            })
        }

    except jsonschema.ValidationError as e:
        logger.error(f"ERROR: JSON Schema Error occurred: {e}")
        response = {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({
                "error": "Invalid start_time or end_time format. Please use the format: YYYY-MM-DD HH:MM:SS.SSS"
            })
        }

    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        response = {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    except Exception as e:
        logger.error(f"ERROR: Internal Server Error: {e}")
        response = {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    return response


def get_transaction_response(result_transactions):
    transaction_response = []
    for txn in result_transactions:
        txn_dict = {
            "txn_hash": txn[0],
            "status": txn[1],
            "amount": txn[2],
            "type": txn[3],
            "fee": txn[4]
        }
        transaction_response.append(txn_dict)

    return transaction_response


def get_block_response(result_blocks):
    block_response = []
    for block in result_blocks:
        block_dict = {
            "block_hash": block[0],
            "previous_block_hash": block[1],
            "txn_hashes": json.loads(block[2]),
            "total_amount": int(block[3]),
            "total_fee": int(block[4]),
            "txn_cnt": int(block[5]),
            "time_stamp": block[6],
            "miner": block[7]
        }
        block_response.append(block_dict)

    return block_response
