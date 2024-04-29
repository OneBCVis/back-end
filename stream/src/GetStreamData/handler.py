import json
import pymysql
from datetime import datetime
import logging
import os
import boto3
import jsonschema
from redis.cluster import Redis


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

# Redis settings
redis_host = os.environ['REDIS_HOST']
redis_port = os.environ['REDIS_PORT']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

schema = {
    "type": "object",
    "properties": {
        "start_time": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$"
        },
        "end_time": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$"
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
                params["start_time"], '%Y-%m-%d %H:%M:%S')
            datetime.strptime(
                params["end_time"], '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            logger.error(f"ERROR: Invalid date format: {e}")
            return {
                'statusCode': 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                'body': json.dumps('Invalid start_time or end_time format. Please use the format: YYYY-MM-DD HH:MM:SS')
            }

        start_timestamp = int(datetime.strptime(
            params["start_time"] + " +00:00", '%Y-%m-%d %H:%M:%S %z').timestamp())
        end_timestamp = int(datetime.strptime(
            params["end_time"] + " +00:00", '%Y-%m-%d %H:%M:%S %z').timestamp())

        if (start_timestamp >= end_timestamp):
            logger.error("ERROR: start_time %s should be less than end_time %s",
                         params["start_time"], params["end_time"])
            return {
                'statusCode': 400,
                "headers": {
                    "Content-Type": "application/json"
                },
                'body': json.dumps('start_time should be less than end_time')
            }

        unavailable = []
        transactions = []
        blocks = []
        redis_client = Redis(host=redis_host, port=redis_port)
        logger.info("SUCCESS: Redis Cluster connection created")
        for i in range(start_timestamp, end_timestamp):
            if redis_client.exists(i):
                logger.info(
                    f"INFO: Data is available in Redis for timestamp: {i}")
                data = json.loads(redis_client.get(i).decode("utf-8"))
                transactions += data["transactions"]
                blocks += data["blocks"]
            else:
                unavailable.append(i)

        if (len(unavailable) > 0):
            logger.info(
                f"INFO: Data is not available in Redis for timestamps: {unavailable}. Fetching data from RDS.")

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

            for i in unavailable:
                query_get_transactions = """
                    SELECT t.txn_hash, t.status, t.amount, t.type, t.fee
                    FROM transaction t
                    WHERE t.insert_time >= %s AND t.insert_time  < %s"""
                cursor.execute(query_get_transactions,
                               (i * 1000, (i + 1) * 1000))
                result_transactions = get_transaction_response(
                    cursor.fetchall())
                transactions += result_transactions

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
                cursor.execute(query_get_blocks, (i * 1000, (i + 1) * 1000))
                result_blocks = get_block_response(cursor.fetchall())
                blocks += result_blocks

                redis_client.set(
                    i, json.dumps({"transactions": result_transactions, "blocks": result_blocks}))
                logger.info(
                    f"INFO: Data stored in Redis for timestamp: {i}")

            cursor.close()
            conn.close()

        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "transactions": transactions,
                "blocks": blocks
            })
        }

    except jsonschema.ValidationError as e:
        logger.error(f"ERROR: JSON Schema Error occurred: {e}")
        response = {
            "statusCode": 400,
            "headers": headers,
            "body": json.dumps({
                "error": "Invalid start_time or end_time format. Please use the format: YYYY-MM-DD HH:MM:SS"
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
