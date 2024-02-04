import json
import pymysql
from datetime import datetime
import logging
import os


# rds settings 
# TODO: Use AWS Secrets Manager to store credentials
user_name = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
rds_proxy_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']

logger = logging.getLogger()
logger.setLevel(logging.INFO)
    

def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))
    return get_real_time_data(event)

def get_real_time_data(event):
    try:
        body = json.loads(json.loads(event['body']))
        last_timestamp = body['last_timestamp']
        
        date_time_obj = datetime.utcfromtimestamp(last_timestamp)
        
        conn = pymysql.connect(rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
        print("SUCCESS: Connection to RDS mysql instance succeeded")
        
        cursor = conn.cursor()
        
        query_get_transactions = "SELECT * FROM transaction WHERE insert_time > ?"
        cursor.execute(query_get_transactions, (date_time_obj))
        result_transactions = cursor.fetchall()
        
        query_get_blocks = "SELECT b.block_hash, bt.txn_hash FROM block b JOIN block_txn bt ON b.block_hash = bt.block_hash WHERE b.insert_time > ?" 
        cursor.execute(query_get_blocks, (date_time_obj))
        result_blocks = cursor.fetchall()
                
        cursor.close()
        conn.close()
        
        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({'transactions': result_transactions,
                                'blocks': format_blocks(result_blocks)})
        }
        
        return response
    
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({"error": str(e)})
        }


def format_blocks(result_blocks):
    blocks_dict = {}
    for block_hash, txn_hash in result_blocks:
        if block_hash not in blocks_dict:
            blocks_dict[block_hash] = []
        blocks_dict[block_hash].append(txn_hash)
    return blocks_dict
