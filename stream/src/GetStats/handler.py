import json
import pymysql
import logging
import os
import base64
from datetime import datetime, timedelta


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
    return get_stats(event)

# # of transactions in last hour
# # of blocks in last hour
# total transactions amount of last hour
# miners of the last 1000 blocks

# create table if not exists transaction
# (
#     txn_hash    varchar(128)                            not null,
#     status      enum('PENDING', 'APPROVED', 'REJECTED') not null default 'PENDING',
#     amount      int(16)                                 not null,
#     insert_time timestamp                               not null default current_timestamp,
#     primary key (txn_hash)
# );

def get_stats(event):
    try:
        body = json.loads(base64.b64decode(event['body']))
        start_time = body['start_time']

        # get timestamp 1h back
        start_time_obj = datetime.strptime(start_time, '%Y-%m-%d %H.%M.%S')
        end_time_obj  = start_time_obj - timedelta(hours=1)
        end_time = end_time_obj.strftime('%Y-%m-%d %H.%M.%S') 
        
        # Connect to the database
        conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)

        cursor = conn.cursor()

        logger.info("SUCCESS: Able to connect to RDS MySQL instance")

        # Numer of transactions in last hour
        query_transactions_in_last_hour= "SELECT COUNT(t.txn_hash) FROM transaction t WHERE t.insert_time >= %s AND t.insert_time <= %s"
        cursor.execute(query_transactions_in_last_hour, (start_time, end_time))
        result_transaction = cursor.fetchall()

        # Numer of blocks in last hour
        query_blocks_in_last_hour = "SELECT COUNT(b.block_hash) FROM block b WHERE b.insert_time >= %s AND b.insert_time <= %s"
        cursor.execute(query_blocks_in_last_hour, (start_time, end_time))
        result_block = cursor.fetchall()

        # Total transactions amount of last hour
        query_total_transactions_amount = "SELECT SUM(t.amount) FROM transaction t WHERE insert_time >= %s AND insert_time <= %s"
        cursor.execute(query_total_transactions_amount, (start_time, end_time))
        result_total_transactions_amount = cursor.fetchall()

        # Miners of the last 1000 blocks with group the repetitive miners and get the best 5 miners .
        query_miners_of_last_1000_blocks = "SELECT miner, COUNT(miner) AS miner_count FROM (SELECT b.miner FROM block b ORDER BT b.insert_time DESC LIMIT 1000) AS recent_blocks GROUP BY miner ORDER BY miner_count DESC LIMIT 5"
        cursor.execute(query_miners_of_last_1000_blocks)
        result_miners = cursor.fetchall()

        cursor.close()

        conn.close()

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "transaction_count": result_transaction[0],
                "block_count": result_block[0],
                "total_tx_amount": result_total_transactions_amount[0],
                "miners" : result_miners[0]
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
        logger.error(f"ERROR: Error occurred: {e}")
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


