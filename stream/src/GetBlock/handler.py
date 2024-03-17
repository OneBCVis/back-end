import json
import pymysql
import logging
import os
import boto3
import jsonschema


# RDS settings
rds_secret_arn = os.environ['RDS_SECRETARN']
rds_proxy_host = os.environ['RDS_HOSTNAME']
db_name = os.environ['RDS_DB_NAME']
region = os.environ['RDS_REGION']

logger = logging.getLogger()
logger.setLevel(logging.INFO)

schema = {
    "type": "object",
    "properties": {
        "block_hash": {
            "type": "string",
            "pattern": "^0x[a-f0-9]{24,128}$"
        }
    },
    "required": ["block_hash"]
}


def handler(event, context):
    # Log the event argument for debugging and for use in local development.
    return get_data_from_rds(event)


def get_data_from_rds(event):
    try:
        jsonschema.validate(event["pathParameters"], schema)
        block_hash = event["pathParameters"]["block_hash"]
        is_full = False

        if event["queryStringParameters"] and "full" in event["queryStringParameters"]:
            is_full = event["queryStringParameters"]["full"] == "true"

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

        if is_full:
            query_get_full_block = """
                SELECT
                    b.block_hash,
                    b.previous_block_hash,
                    b.total_amount,
                    b.total_fee,
                    b.txn_count,
                    b.time_stamp,
                    b.miner,
                    b.nonce,
                    b.difficulty,
                    b.height,
                    (
                        SELECT JSON_ARRAYAGG(txn_hash)
                        FROM block_txn
                        WHERE block_hash = b.block_hash
                    ) AS transactions,
                    (
                        SELECT JSON_ARRAYAGG(uncle_hash)
                        FROM uncle
                        WHERE block_hash = b.block_hash
                    ) AS uncles,
                    (
                        SELECT JSON_ARRAYAGG(JSON_OBJECT('id', id, 'size', size))
                        FROM off_chain_data
                        WHERE block_hash = b.block_hash
                    ) AS sidecar
                FROM
                    block b
                WHERE
                    b.block_hash = %s"""
            cursor.execute(query_get_full_block, (block_hash))
        else:
            query_get_block_header = """
                SELECT
                    b.block_hash,
                    b.previous_block_hash,
                    b.total_amount,
                    b.total_fee,
                    b.txn_count,
                    b.time_stamp,
                    b.miner,
                    b.nonce,
                    b.difficulty,
                    b.height
                FROM
                    block b
                WHERE
                    b.block_hash = %s"""
            cursor.execute(query_get_block_header, (block_hash))

        result_block = cursor.fetchall()

        cursor.close()

        conn.close()

        if (len(result_block) == 0):
            logger.error(f"ERROR: Block hash {block_hash} not found")
            response = {
                "statusCode": 404,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({
                    "error": "Block hash not found"
                })
            }
        else:
            response = {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps(
                    get_full_block_response(
                        result_block[0]) if is_full else get_block_header_response(result_block[0])
                )
            }

    except jsonschema.ValidationError as e:
        logger.error(f"ERROR: JSON Schema Error occurred: {e}")
        response = {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Invalid block hash"
            })
        }

    except pymysql.MySQLError as e:
        logger.error(f"ERROR: MySQL Error occurred: {e}")
        response = {
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
        response = {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "error": "Internal Server Error"
            })
        }

    return response


def get_full_block_response(result_block):
    block_dict = {
        "block_hash": result_block[0],
        "previous_block_hash": result_block[1],
        "total_amount": int(result_block[2]),
        "total_fee": int(result_block[3]),
        "txn_count": int(result_block[4]),
        "time_stamp": result_block[5],
        "miner": result_block[6],
        "nonce": result_block[7],
        "difficulty": result_block[8],
        "height": result_block[9],
        "transactions": json.loads(result_block[10]),
        "uncles": json.loads(result_block[11]),
        "sidecar": json.loads(result_block[12])
    }

    return block_dict


def get_block_header_response(result_block):
    block_dict = {
        "block_hash": result_block[0],
        "previous_block_hash": result_block[1],
        "total_amount": int(result_block[2]),
        "total_fee": int(result_block[3]),
        "txn_count": int(result_block[4]),
        "time_stamp": result_block[5],
        "miner": result_block[6],
        "nonce": result_block[7],
        "difficulty": result_block[8],
        "height": result_block[9]
    }

    return block_dict