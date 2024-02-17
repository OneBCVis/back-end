import base64
import json
import logging
import pymysql
import os


# Schema of a block:
# {
#     Hash: String,
#     PreviousBlockHash: String,
#     Timestamp: String,
#     Miner: String | "",
#     Transactions: List<String>
# }

# TODO: Use AWS Secrets Manager to store credentials

user_name = os.environ['RDS_USERNAME']
password = os.environ['RDS_PASSWORD']
rds_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']
port = os.environ['RDS_PORT']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(host=rds_host, user=user_name, passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    exit(1)


def handler(event, context):
    process_blocks(event["Records"])

    return {}


def process_blocks(records):
    with conn.cursor() as cur:
        for record in records:
            try:
                block = json.loads(record["body"])
                sql_insert_block = "INSERT INTO block (block_hash, previous_block_hash, timestamp, miner) VALUES (%s, %s, %s, %s)"
                cur.execute(sql_insert_block, (block["Hash"], block["PreviousBlockHash"], block["Timestamp"], block["Miner"]))

                for txn in block["Transactions"]:
                    sql_insert_txn = "INSERT INTO block_txn (block_hash, txn_hash) VALUES (%s, %s)"
                    cur.execute(sql_insert_txn, (block["Hash"], txn))
                    sql_update_txn_status = "UPDATE transaction SET status = %s WHERE txn_hash = %s"
                    cur.execute(sql_update_txn_status, ("APPROVED", txn))

                logger.info(f"INFO: Inserted block with hash: {block['Hash']}")
                conn.commit()
            except pymysql.IntegrityError as e:
                if e.args[0] == 1062:
                    logger.info(f"INFO: Duplicate block with hash: {block['Hash']}. Skipping insert")
                else:
                    logger.error(f"ERROR: MySQL Error occurred: {e}")
                    conn.rollback()
            except pymysql.MySQLError as e:
                logger.error(f"ERROR: MySQL Error occurred: {e}")
                conn.rollback()
            except Exception as e:
                logger.error(f"ERROR: Could not process block: {e}")
                conn.rollback()
    conn.commit()
