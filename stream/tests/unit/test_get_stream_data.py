# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_stream_data import get_stream_data


data = get_stream_data()
mock_event = data["event"]
mock_txns = data["txns"]
mock_blocks = data["blocks"]
body = json.loads(mock_event['body'])
calls = []

rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.side_effect = [mock_txns, mock_blocks]


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock:
        rds_mock.return_value = rds_conn_mock

        from src.GetStreamData.handler import handler
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 2
        assert mock_cursor.fetchall.call_count == 2

        assert response["statusCode"] == 200
        assert response["headers"] == {
            "Content-Type": "application/json"
        }
        assert json.loads(response["body"]) == {
            "transactions": [
                {
                    "txn_hash": mock_txns[0][0],
                    "status": mock_txns[0][1],
                    "amount": mock_txns[0][2]
                },
                {
                    "txn_hash": mock_txns[1][0],
                    "status": mock_txns[1][1],
                    "amount": mock_txns[1][2]
                },
                {
                    "txn_hash": mock_txns[2][0],
                    "status": mock_txns[2][1],
                    "amount": mock_txns[2][2]
                }

            ],
            "blocks": [
                {
                    "block_hash": mock_blocks[0][0],
                    "previous_block_hash": mock_blocks[0][1],
                    "txn_hashes": mock_blocks[0][2].split(",")
                }
            ]
        }

        calls.append(call(
            "SELECT t.txn_hash, t.status, t.amount FROM transaction t WHERE t.insert_time >= %s AND t.insert_time  < %s",
            (body["start_time"], body["end_time"])
        ))

        calls.append(call(
            "SELECT b.block_hash, b.previous_block_hash, GROUP_CONCAT(bt.txn_hash) FROM block b JOIN block_txn bt ON b.block_hash = bt.block_hash WHERE b.insert_time >= %s AND b.insert_time < %s GROUP BY b.block_hash",
            (body["start_time"], body["end_time"])
        ))

        mock_execute.assert_has_calls(calls, any_order=True)
