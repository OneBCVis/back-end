import json
import pymysql
from datetime import datetime
import logging
import os


# RDS settings
# TODO: Use AWS Secrets Manager to store credentials
user_name = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
rds_proxy_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']

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
        
        # Connect to the database
        conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
        
        cursor = conn.cursor()
        
        logger.info("SUCCESS: Able to connect to RDS MySQL instance")

        query_get_transactions = "SELECT t.txn_hash, t.status, t.amount FROM transaction t WHERE t.insert_time >= %s AND t.insert_time  < %s"
        cursor.execute(query_get_transactions, (start_timestamp, end_timestamp))
        result_transactions = cursor.fetchall()
        
        query_get_blocks = "SELECT b.block_hash, b.previous_block_hash, GROUP_CONCAT(bt.txn_hash) FROM block b JOIN block_txn bt ON b.block_hash = bt.block_hash WHERE b.insert_time >= %s AND b.insert_time < %s GROUP BY b.block_hash"
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
        response =  {
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
        response =  {
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
            "amount": txn[2]
        }
        transaction_response.append(txn_dict)

    return transaction_response


def get_block_response(result_blocks):
    block_response = []
    for block in result_blocks:
        block_dict = {
            "block_hash": block[0],
            "previous_block_hash": block[1],
            "txn_hashes": block[2].split(",")
        }
        block_response.append(block_dict)

    return block_response
