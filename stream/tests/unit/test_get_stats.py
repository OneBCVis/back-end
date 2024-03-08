# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_stats import get_stats


data = get_stats()
mock_event = data["event"]


rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.side_effect = [
    [(data["transaction_count"],)],
    [(data["block_count"],)],
    [(data["total_tx_amount"],)],
    data["miners"]
]
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}
calls = []


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        from src.GetStats.handler import handler
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 4
        assert mock_cursor.fetchall.call_count == 4

        assert response["statusCode"] == 200
        assert response["headers"] == {
            "Content-Type": "application/json"
        }
        assert json.loads(response["body"]) == {
            "transaction_count": data["transaction_count"],
            "block_count": data["block_count"],
            "total_tx_amount": data["total_tx_amount"],
            "miners": data["miners"]
        }

        calls.append(call(
            "SELECT COUNT(t.txn_hash) FROM transaction t WHERE t.insert_time >= %s AND t.insert_time <= %s",
            (data["end_time"], data["start_time"])
        ))

        calls.append(call(
            "SELECT COUNT(b.block_hash) FROM block b WHERE b.insert_time >= %s AND b.insert_time <= %s",
            (data["end_time"], data["start_time"])
        ))

        calls.append(call(
            "SELECT SUM(t.amount) FROM transaction t WHERE insert_time >= %s AND insert_time <= %s",
            (data["end_time"], data["start_time"])
        ))

        calls.append(call(
            '''SELECT miner, COUNT(miner) AS miner_count FROM 
                                              (SELECT b.miner FROM block b ORDER BY b.insert_time DESC LIMIT 1000) AS recent_blocks 
                                              GROUP BY miner ORDER BY miner_count DESC LIMIT 5'''
        ))

        mock_execute.assert_has_calls(calls, any_order=True)
