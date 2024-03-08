import json
import pymysql
from datetime import datetime
import logging
import os
import boto3


# RDS settings
rds_secret_arn = os.environ['RDS_SECRETARN']
rds_proxy_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']
region = os.environ['RDS_REGION']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    return get_data_from_rds(event)


def get_data_from_rds(event):
    try:
        body = json.loads(event['body'])
        start_timestamp = body['start_time']
        end_timestamp = body['end_time']

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
                bt.txn_hashes,
                u.uncle_hashes,
                ocd.off_chain_data_ids,
                ocd.off_chain_data_sizes
            FROM
                block b
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(txn_hash) txn_hashes
                FROM
                    block_txn
                GROUP BY
                    block_hash
            ) bt ON b.block_hash = bt.block_hash
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(uncle_hash) uncle_hashes
                FROM
                    uncle
                GROUP BY
                    block_hash
            ) u ON b.block_hash = u.block_hash
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(id) off_chain_data_ids,
                    GROUP_CONCAT(size) off_chain_data_sizes
                FROM
                    off_chain_data
                GROUP BY
                    block_hash
            ) ocd ON b.block_hash = ocd.block_hash
            WHERE
                b.insert_time >= %s AND b.insert_time < %s"""
        cursor.execute(query_get_blocks, (start_timestamp, end_timestamp))
        result_blocks = cursor.fetchall()

        cursor.close()
        conn.close()

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "transactions": get_transaction_response(result_transactions),
                "blocks": get_block_response(result_blocks)
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
        logger.error(f"ERROR: Internal Server Error: {e}")
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
            "txn_hashes": block[2].split(",") if block[2] else [],
            "uncle_hashes": block[3].split(",") if block[3] else [],
            "off_chain_data_ids": block[4].split(",") if block[4] else [],
            "off_chain_data_sizes": list(map(int, block[5].split(","))) if block[5] else []
        }
        block_response.append(block_dict)

    return block_response
