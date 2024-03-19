# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_block import get_block


data = get_block()
mock_event = data["event"]
mock_block = data["block"]
mock_initial_blocks = data["initial_blocks"]


def block_dict_to_list(block_dict, full=False):
    lst = [
        block_dict["block_hash"],
        block_dict["previous_block_hash"],
        block_dict["total_amount"],
        block_dict["total_fee"],
        block_dict["txn_count"],
        block_dict["time_stamp"],
        block_dict["miner"],
        block_dict["nonce"],
        block_dict["difficulty"],
        block_dict["height"]
    ]
    if full:
        lst.append(json.dumps(block_dict["transactions"]))
        lst.append(json.dumps(block_dict["uncles"]))
        lst.append(json.dumps(block_dict["sidecar"]))
    return lst


rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.side_effect = [
    [block_dict_to_list(mock_block)],
    [block_dict_to_list(mock_block)],
    [block_dict_to_list(mock_block, True)],
    [block_dict_to_list(block) for block in mock_initial_blocks]
]
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}

mock_block_header = {
    "block_hash": mock_block["block_hash"],
    "previous_block_hash": mock_block["previous_block_hash"],
    "total_amount": mock_block["total_amount"],
    "total_fee": mock_block["total_fee"],
    "txn_count": mock_block["txn_count"],
    "time_stamp": mock_block["time_stamp"],
    "miner": mock_block["miner"],
    "nonce": mock_block["nonce"],
    "difficulty": mock_block["difficulty"],
    "height": mock_block["height"]
}
calls = []


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        from src.GetBlock.handler import handler, headers
        response_1 = handler(mock_event, None)
        mock_event["queryStringParameters"] = {"full": "false"}
        response_2 = handler(mock_event, None)
        mock_event["queryStringParameters"]["full"] = "true"
        response_3 = handler(mock_event, None)
        mock_event["queryStringParameters"] = None
        mock_event["pathParameters"] = {"block_hash": "initial"}
        response_4 = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 4
        assert mock_cursor.fetchall.call_count == 4
        calls.append(call("""
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
                    b.block_hash = %s""", mock_block["block_hash"]))
        calls.append(call("""
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
                    b.block_hash = %s""", mock_block["block_hash"]))
        calls.append(call("""
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
                    b.block_hash = %s""", mock_block["block_hash"]))
        calls.append(call("""
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
                ORDER BY
                    b.insert_time DESC
                LIMIT 5"""))
        mock_execute.assert_has_calls(calls, any_order=True)

        assert response_1["statusCode"] == 200
        assert response_1["headers"] == headers
        assert json.loads(response_1["body"]) == mock_block_header

        assert response_2["statusCode"] == 200
        assert response_2["headers"] == headers
        assert json.loads(response_2["body"]) == mock_block_header

        assert response_3["statusCode"] == 200
        assert response_3["headers"] == headers
        assert json.loads(response_3["body"]) == mock_block

        assert response_4["statusCode"] == 200
        assert response_4["headers"] == headers
        assert json.loads(response_4["body"]) == {
            "blocks": mock_initial_blocks}
