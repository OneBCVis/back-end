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
    conn = pymysql.connect(host=rds_host, user=user_name,
                           passwd=password, db=db_name, connect_timeout=5)
except pymysql.MySQLError as e:
    logger.error(
        "ERROR: Unexpected error: Could not connect to MySQL instance.")
    logger.error(e)
    exit(1)


def handler(event, context):
    process_records(event["Records"])

    return {}


def process_records(records):
    try:
        with conn.cursor() as cur:
            for record in records:
                message, message_type, message_data = None, None, None
                try:
                    message = json.loads(
                        base64.b64decode(record["kinesis"]["data"]))
                    message_type = message['type']
                    message_data = message['data']
                except Exception as e:
                    logger.error(f"ERROR: Could not decode message: {e}")
                    continue
                if message_type == 'TRANSACTION':
                    process_transaction(message_data, cur)
                elif message_type == 'BLOCK':
                    process_block(message_data, cur)
                else:
                    logger.error(f"ERROR: Unknown record type: {message_type}")
        conn.close()
    except Exception as e:
        logger.error(f"ERROR: Could not process records: {e}")
        if (conn.open):
            conn.rollback()
            conn.close()


def process_transaction(txn, cur):
    try:
        sql_insert_txn = """INSERT INTO transaction (txn_hash, status, amount, type, nonce, fee)
                            VALUES (%s, %s, %s, %s, %s, %s)"""

        cur.execute(sql_insert_txn, (
            txn["Hash"],
            txn["Status"],
            txn["Amount"],
            txn["Type"],
            txn["Nonce"],
            txn["Fee"]
        ))

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
            logger.info(
                "INFO: Duplicate transaction with hash: %s. Skipping insert".format(txn['Hash']))
            conn.rollback()
        else:
            logger.error(f"ERROR: SQL Integrity Error occurred: {e}")
            conn.rollback()
    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        conn.rollback()
    except Exception as e:
        logger.error(f"ERROR: Could not process transaction: {e}")
        conn.rollback()


def process_block(block, cur):
    try:
        sql_insert_block = """INSERT INTO block
                                (block_hash, previous_block_hash, height, nonce, difficulty, miner, time_stamp)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cur.execute(sql_insert_block, (
            block["Hash"],
            block["PreviousBlockHash"],
            block["Height"],
            block["Nonce"],
            block["Difficulty"],
            block["Miner"],
            block["Timestamp"]
        ))

        for txn in block["Transactions"]:
            sql_insert_txn = "INSERT INTO block_txn (block_hash, txn_hash) VALUES (%s, %s)"
            cur.execute(sql_insert_txn, (block["Hash"], txn))
            sql_update_txn_status = "UPDATE transaction SET status = %s WHERE txn_hash = %s"
            cur.execute(sql_update_txn_status, ("APPROVED", txn))

        for uncle in block["Uncles"]:
            sql_insert_uncle = "INSERT INTO uncle (uncle_hash, block_hash) VALUES (%s, %s)"
            cur.execute(sql_insert_uncle, (uncle, block["Hash"]))

        for offChainData in block["Sidecar"]:
            sql_insert_off_chain = """INSERT INTO off_chain_data
                                        (block_hash, id, transaction_id, size)
                                        VALUES (%s, %s, %s, %s)"""
            cur.execute(sql_insert_off_chain, (
                block["Hash"],
                offChainData["ID"],
                offChainData["TransactionID"],
                offChainData["Size"]
            ))

        logger.info(f"INFO: Inserted block with hash: {block['Hash']}")
        conn.commit()
    except pymysql.IntegrityError as e:
        if (e.args[0] == 1062):
            logger.info(
                "INFO: Duplicate block with hash: %s. Skipping insert".format(block['Hash']))
        else:
            logger.error(f"ERROR: SQL Integrity Error occurred: {e}")
            conn.rollback()
    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        conn.rollback()
    except Exception as e:
        logger.error(f"ERROR: Could not process block: {e}")
        conn.rollback()
