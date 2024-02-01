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

                if (not isinstance(txn["Sender"], list)) or (not isinstance(txn["Receiver"], list)):
                    logger.error(f"ERROR: Unexpected error: Sender and Receiver should be arrays of transaction: {txn["Hash"]}. Skipping insert")
                    continue

                if txn["Status"] not in ("Pending", "Approved", "Rejected"):
                    logger.error(f"ERROR: Unexpected error: Status should be one of (Pending, Approved, Rejected): {txn['Status']}")
                    continue

                if not isinstance(txn["Amount"], int):
                    logger.error(f"ERROR: Unexpected error: Amount should be an integer: {txn['Amount']}")
                    continue

                if txn["Amount"] < 0:
                    logger.error(f"ERROR: Unexpected error: Amount should be either a positive number or zero: {txn['Amount']}")
                    continue
            except Exception as e:
                logger.error(f"ERROR: Unexpected error: Could not parse transaction: {e}")
                continue

            sql_insert_txn = "INSERT INTO transaction (txn_hash, status, amount) VALUES (%s, %s, %s)"
            try:
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
                if e.args[0] == pymysql.constants.ER.DUP_ENTRY:
                    logger.info(f"INFO: Duplicate transaction with hash: {txn['Hash']}. Skipping insert")
                    conn.rollback()
                else:
                    logger.error(f"ERROR: SQL Integrity Error occurred: {e}")
                    conn.rollback()
            except Exception as e:
                logger.error(f"ERROR: Unexpected error occurred: {e}")
                conn.rollback()
    conn.commit()
