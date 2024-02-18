import base64
import json
import logging
import pymysql
import os


# Schema of a transaction:
# {
#     Hash: String,
#     Sender: List<String>,
#     Receiver: List<String>
#     Status: One of { "Pending", "Approved", "Rejected" }
#     Amount: Integer,
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
    process_transactions(event["Records"])

    return {}


def process_transactions(records):
    with conn.cursor() as cur:
        for record in records:
            try:
                txn = json.loads(base64.b64decode(record["kinesis"]["data"]))
                sql_insert_txn = "INSERT INTO transaction (txn_hash, status, amount) VALUES (%s, %s, %s)"
                cur.execute(sql_insert_txn, (txn["Hash"], txn["Status"], txn["Amount"]))

                for sender in txn["Sender"]:
                    sql_insert_sender = "INSERT INTO txn_sender (txn_hash, sender_key) VALUES (%s, %s)"
                    cur.execute(sql_insert_sender, (txn["Hash"], sender))

                for receiver in txn["Receiver"]:
                    sql_insert_receiver = "INSERT INTO txn_receiver (txn_hash, receiver_key) VALUES (%s, %s)"
                    cur.execute(sql_insert_receiver, (txn["Hash"], receiver))

                logger.info(f"INFO: Inserted transaction with hash: {txn['Hash']}")
                conn.commit()
            except pymysql.IntegrityError as e:
                if e.args[0] == 1062:
                    logger.info(f"INFO: Duplicate transaction with hash: {txn['Hash']}. Skipping insert")
                    conn.rollback()
                else:
                    logger.error(f"ERROR: MySQL Error occurred: {e}")
                    conn.rollback()
            except pymysql.MySQLError as e:
                logger.error(f"ERROR: MySQL Error occurred: {e}")
                conn.rollback()
            except Exception as e:
                logger.error(f"ERROR: Could not process transaction: {e}")
                conn.rollback()
    conn.commit()
