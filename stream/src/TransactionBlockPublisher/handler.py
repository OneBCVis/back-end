import base64
import json
import logging
import pymysql
import os
import boto3


# Schema of a transaction:
# {
#     Hash: String,
#     Sender: List<String>,
#     Receiver: List<String>
#     Status: One of { "Pending", "Approved", "Rejected" }
#     Amount: Integer,
#     Type: Integer,
#     Nonce: Integer,
#     Fee: Integer
# }

# Schema of a block:
# {
#     Hash: String,
#     PreviousBlockHash: String,
#     Height: Integer,
#     Nonce: Integer,
#     Difficulty: Integer,
#     Timestamp: String,
#     Miner: String | "",
#     Transactions: List<Transaction>
# }

rds_secret_arn = os.environ['RDS_SECRETARN']
rds_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']
port = os.environ['RDS_PORT']
region = os.environ['RDS_REGION']

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        client = boto3.client(
            service_name='secretsmanager', region_name=region)
        response = client.get_secret_value(SecretId=rds_secret_arn)
        secret = json.loads(response["SecretString"])
        user_name = secret["username"]
        password = secret["password"]
        conn = pymysql.connect(host=rds_host, user=user_name,
                               passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error(
            "ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        exit(1)
    except Exception as e:
        logger.error("ERROR: Unexpected error.")
        logger.error(e)
        exit(1)

    process_records(event["Records"], conn)

    return {}


def process_records(records, conn):
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
                    process_transaction(message_data, conn, cur)
                elif message_type == 'BLOCK':
                    process_block(message_data, conn, cur)
                else:
                    logger.error(f"ERROR: Unknown record type: {message_type}")
        conn.close()
    except Exception as e:
        logger.error(f"ERROR: Could not process records: {e}")
        if (conn.open):
            conn.rollback()
            conn.close()


def process_transaction(txn, conn, cur, is_full=False):
    try:
        sql_insert_txn = "call insert_transaction(%s, %s, %s, %s, %s, %s, %s, %s, %s, @result)"

        cur.execute(sql_insert_txn, (
            txn["Hash"],
            txn["Status"],
            txn["Amount"],
            txn["Type"],
            txn["Nonce"],
            txn["Fee"],
            json.dumps(txn["Sender"]),
            json.dumps(txn["Receiver"]),
            is_full
        ))

        cur.execute("SELECT @result AS result")
        result = cur.fetchone()[0]

        if result == 0:
            logger.info(
                f"INFO: Inserted transaction with hash: {txn['Hash']}")
        elif result == 1:
            logger.info(
                f"INFO: Updated transaction with hash: {txn['Hash']}")
        elif result == 2:
            logger.info(
                f"INFO: Duplicate transaction with hash: {txn['Hash']}. Skipping insert")
        else:
            logger.error(
                f"ERROR: Could not process transaction: {txn['Hash']}")

        conn.commit()
        return txn['Amount'], txn['Fee']
    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        conn.rollback()
    except Exception as e:
        logger.error(f"ERROR: Could not process transaction: {e}")
        conn.rollback()

    return None, None


def process_block(block, conn, cur):
    try:
        total_amount, total_fee, txn_cnt = 0, 0, len(block["Transactions"])
        for txn in block["Transactions"]:
            amount, fee = process_transaction(txn, conn, cur, True)
            if (amount != None) and (fee != None):
                total_amount += int(amount)
                total_fee += int(fee)

        sql_insert_block = """INSERT INTO block
                                (block_hash, previous_block_hash, height, nonce, difficulty,
                                miner, time_stamp, total_amount, total_fee, txn_count)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

        cur.execute(sql_insert_block, (
            block["Hash"],
            block["PreviousBlockHash"],
            block["Height"],
            block["Nonce"],
            block["Difficulty"],
            block["Miner"],
            block["Timestamp"],
            total_amount,
            total_fee,
            txn_cnt
        ))

        for txn in block["Transactions"]:
            sql_insert_txn = "INSERT INTO block_txn (block_hash, txn_hash) VALUES (%s, %s)"
            cur.execute(sql_insert_txn, (block["Hash"], txn["Hash"]))

        for uncle in block["Uncles"]:
            sql_insert_uncle = "INSERT INTO uncle (uncle_hash, block_hash) VALUES (%s, %s)"
            cur.execute(sql_insert_uncle, (uncle, block["Hash"]))

        for offChainData in block["Sidecar"]:
            sql_insert_off_chain = """INSERT INTO off_chain_data
                                        (block_hash, id, txn_id, size)
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
                "INFO: Duplicate block with hash: {}. Skipping insert".format(block['Hash']))
        else:
            logger.error(f"ERROR: SQL Integrity Error occurred: {e}")
            conn.rollback()
    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        conn.rollback()
    except Exception as e:
        logger.error(f"ERROR: Could not process block: {e}")
        conn.rollback()
