import json
import pymysql
import logging
import os
import boto3
from datetime import datetime, timedelta


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


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    return get_stats(event)


def get_stats(event):
    try:
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

        query_stats_in_last_hour = """
            SELECT
                SUM(b.txn_count) AS transaction_count,
                COUNT(b.block_hash) AS block_count,
                SUM(b.total_amount) AS total_tx_amount,
                SUM(b.total_fee) AS total_tx_fee
            FROM
                block b
            WHERE
                b.insert_time >= (CURRENT_TIMESTAMP(3) - INTERVAL 1 HOUR)
                AND b.insert_time <= CURRENT_TIMESTAMP(3)"""
        cursor.execute(query_stats_in_last_hour)
        result_stats = cursor.fetchall()

        # Miners of the last 1000 blocks with group the repetitive miners and get the best 5 miners .
        query_miners_of_last_1000_blocks = """
            SELECT
                miner,
                COUNT(miner) AS miner_count
            FROM
                (
                    SELECT b.miner
                    FROM block b
                    ORDER BY b.insert_time DESC
                    LIMIT 1000
                ) AS recent_blocks
            GROUP BY
                miner
            ORDER BY
                miner_count DESC
            LIMIT 5"""
        cursor.execute(query_miners_of_last_1000_blocks)
        result_miners = cursor.fetchall()

        query_txn_pool = """
            SELECT
                COUNT(txn_hash) AS txn_count
            FROM
                transaction
            WHERE
                status = 'PENDING'"""
        cursor.execute(query_txn_pool)
        result_txn_pool = cursor.fetchall()

        cursor.close()

        conn.close()

        response = {
            "statusCode": 200,
            "headers": headers,
            "body": json.dumps({
                "transaction_count": int(result_stats[0][0]) if len(result_stats) > 0 and result_stats[0][0] != None else 0,
                "block_count": int(result_stats[0][1]) if len(result_stats) > 0 and result_stats[0][1] != None else 0,
                "total_tx_amount": int(result_stats[0][2]) if len(result_stats) > 0 and result_stats[0][2] != None else 0,
                "total_tx_fee": int(result_stats[0][3]) if len(result_stats) > 0 and result_stats[0][3] != None else 0,
                "txn_pool": int(result_txn_pool[0][0]) if len(result_txn_pool) > 0 and result_txn_pool[0][0] != None else 0,
                "miners": result_miners if len(result_miners) > 0 else []
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
        logger.error(f"ERROR: Error occurred: {e}")
        response = {
            "statusCode": 500,
            "headers": headers,
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    return response
