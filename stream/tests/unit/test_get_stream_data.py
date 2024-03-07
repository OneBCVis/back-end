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
                    "txn_hashes": mock_blocks[0][2].split(","),
                    "uncle_hashes": mock_blocks[0][3].split(","),
                    "off_chain_data_ids": mock_blocks[0][4].split(","),
                    "off_chain_data_sizes": list(map(int, mock_blocks[0][5].split(",")))
                }
            ]
        }

        calls.append(call("""
            SELECT t.txn_hash, t.status, t.amount, t.type, t.fee
            FROM transaction t
            WHERE t.insert_time >= %s AND t.insert_time  < %s""",
                          (body["start_time"], body["end_time"])
                          ))

        calls.append(call("""
            SELECT
                b.block_hash,
                b.previous_block_hash,
                bt.txn_hashes,
                u.uncle_hashes,
                ocd.off_chain_data_ids,
                ocd.off_chain_data_sizes
            FROM
                block b
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(txn_hash) txn_hashes
                FROM
                    block_txn
                GROUP BY
                    block_hash
            ) bt ON b.block_hash = bt.block_hash
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(uncle_hash) uncle_hashes
                FROM
                    uncle
                GROUP BY
                    block_hash
            ) u ON b.block_hash = u.block_hash
            LEFT JOIN (
                SELECT
                    block_hash,
                    GROUP_CONCAT(id) off_chain_data_ids,
                    GROUP_CONCAT(size) off_chain_data_sizes
                FROM
                    off_chain_data
                GROUP BY
                    block_hash
            ) ocd ON b.block_hash = ocd.block_hash
            WHERE
                b.insert_time >= %s AND b.insert_time < %s""",
                          (body["start_time"], body["end_time"])
                          ))

        mock_execute.assert_has_calls(calls, any_order=True)
