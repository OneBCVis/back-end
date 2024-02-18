import json
import pymysql
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
        body = json.loads((event['body']))
        txn_hash = body['txn_hash']

        # Connect to the database
        conn = pymysql.connect(host=rds_proxy_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)

        cursor = conn.cursor()

        logger.info("SUCCESS: Able to connect to RDS MySQL instance")

        query_get_transaction = "SELECT t.txn_hash, t.status, t.amount FROM transaction t WHERE t.txn_hash = %s"
        cursor.execute(query_get_transaction, (txn_hash))
        result_transaction = cursor.fetchall()

        cursor.close()

        conn.close()

        response = {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "txn_hash": result_transaction[0][0],
                "status": result_transaction[0][1],
                "amount": result_transaction[0][2]
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
