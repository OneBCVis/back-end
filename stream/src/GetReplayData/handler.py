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


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))

    return get_data_from_rds(event)


def get_data_from_rds(event):
    try:
        body = json.loads(event['body'])
        start_timestamp = body['start_timestamp']
        end_timestamp = body['end_timestamp']
        
        start_time = datetime.utcfromtimestamp(start_timestamp)
        end_time = datetime.utcfromtimestamp(end_timestamp)
        
        # Connect to the database
        conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
        
        cursor = conn.cursor()
        
        query_get_transactions = "SELECT * FROM transactions t WHERE t.timestamp >= ? AND t.timestamp  <= ?"
        cursor.execute(query_get_transactions, (start_time, end_time))
        result_transactions = cursor.fetchall()
        
        query_get_blocks = "SELECT b.block_hash, bt.txn_hash FROM block b JOIN block_txn bt ON b.block_hash = bt.block_hash WHERE b.insert_time >= ? AND b.insert_time <= ?"
        cursor.execute(query_get_blocks, (start_time, end_time))
        result_blocks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "transactions": result_transactions,
                "blocks": format_blocks(result_blocks)
            })
        }
        
        return response
    
    except Exception as e:
        logging.error(e)
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                # TODO: Have to handle the error messages
                "error": "An error occurred" 
            })
        }
    

def format_blocks(result_blocks):
    block_dict = {}
    for block_hash, txn_hash in result_blocks:
        if block_hash not in block_dict:
            block_dict[block_hash] = []
        block_dict[block_hash].append(txn_hash)
        
    return block_dict
