import json
import pymysql
from datetime import datetime
import logging
import sys

# rds settings (this has to change as per RDS instance data)
user_name = "XXXX"
password = "XXXX"
rds_proxy_host = "XXXX"
db_name = "XXXX"

logger = logging.getLogger()
logger.setLevel(logging.INFO)
    
def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    print(json.dumps(event))
    get_real_time_data(event)

    return {}

def get_real_time_data(event):
    try:
        message = event['Records'][0]['body']
        data = json.loads(message)
        last_timestamp = data['last_timestamp']
        
        date_time_obj = datetime.utcfromtimestamp(last_timestamp)
        
        conn = pymysql.connect(rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
        print("SUCCESS: Connection to RDS mysql instance succeeded")
        
        cursor = conn.cursor()
        
        query_get_transactions = f"SELECT * FROM transaction WHERE insert_time > {date_time_obj}"
        cursor.execute(query_get_transactions)
        result_transactions = cursor.fetchall()
        
        query_get_blocks = f"SELECT b.block_hash, bt.txn_hash FROM block b JOIN block_txn bt ON b.block_hash = bt.block_hash WHERE b.insert_time > {date_time_obj}" 
        cursor.execute(query_get_blocks)
        result_blocks = cursor.fetchall()
                
        cursor.close()
        conn.close()
        
        response = {
            "statusCode": 200,
            "body": json.dumps({'transactions': result_transactions,
                                'blocks': format_blocks(result_blocks)})
        }
        
        return response
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
    
def format_blocks(result_blocks):
    blocks_dict = {}
    for block_hash, txn_hash in result_blocks:
        if block_hash not in blocks_dict:
            blocks_dict[block_hash] = []
        blocks_dict[block_hash].append(txn_hash)
    return blocks_dict