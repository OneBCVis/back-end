# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_stream_data import get_stream_data


data = get_stream_data()
mock_event = data["event"]
mock_txns = data["txns"]
mock_blocks = data["blocks"]
params = mock_event['queryStringParameters']
calls = []

rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.side_effect = [mock_txns, mock_blocks]
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        from src.GetStreamData.handler import handler, headers
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 2
        assert mock_cursor.fetchall.call_count == 2

        assert response["statusCode"] == 200
        assert response["headers"] == headers
        assert json.loads(response["body"]) == {
            "transactions": [
                {
                    "txn_hash": mock_txns[0][0],
                    "status": mock_txns[0][1],
                    "amount": mock_txns[0][2],
                    "type": mock_txns[0][3],
                    "fee": mock_txns[0][4]
                },
                {
                    "txn_hash": mock_txns[1][0],
                    "status": mock_txns[1][1],
                    "amount": mock_txns[1][2],
                    "type": mock_txns[1][3],
                    "fee": mock_txns[1][4]
                },
                {
                    "txn_hash": mock_txns[2][0],
                    "status": mock_txns[2][1],
                    "amount": mock_txns[2][2],
                    "type": mock_txns[2][3],
                    "fee": mock_txns[2][4]
                }

            ],
            "blocks": [
                {
                    "block_hash": mock_blocks[0][0],
                    "previous_block_hash": mock_blocks[0][1],
                    "txn_hashes": json.loads(mock_blocks[0][2]),
                    "total_amount": mock_blocks[0][3],
                    "total_fee": mock_blocks[0][4],
                    "txn_cnt": mock_blocks[0][5],
                    "time_stamp": mock_blocks[0][6],
                    "miner": mock_blocks[0][7]
                }
            ]
        }

        calls.append(call("""
            SELECT t.txn_hash, t.status, t.amount, t.type, t.fee
            FROM transaction t
            WHERE t.insert_time >= %s AND t.insert_time  < %s""",
                          (params["start_time"], params["end_time"])
                          ))

        calls.append(call("""
            SELECT
                b.block_hash,
                b.previous_block_hash,
                JSON_ARRAYAGG(bt.txn_hash) AS transactions,
                b.total_amount,
                b.total_fee,
                b.txn_count,
                b.time_stamp,
                b.miner
            FROM
                block b
            LEFT JOIN block_txn bt ON b.block_hash = bt.block_hash
            WHERE
                b.insert_time >= %s AND b.insert_time < %s
            GROUP BY
                b.block_hash""",
                          (params["start_time"], params["end_time"])
                          ))

        mock_execute.assert_has_calls(calls, any_order=True)
