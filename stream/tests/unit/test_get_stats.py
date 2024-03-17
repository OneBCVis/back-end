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
    [(data["transaction_count"], data["block_count"],
      data["total_tx_amount"], data["total_tx_fee"])],
    data["miners"],
    [(data["txn_pool"],)]
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

        from src.GetStats.handler import handler, headers
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 3
        assert mock_cursor.fetchall.call_count == 3

        assert response["statusCode"] == 200
        assert response["headers"] == headers
        assert json.loads(response["body"]) == {
            "transaction_count": data["transaction_count"],
            "block_count": data["block_count"],
            "total_tx_amount": data["total_tx_amount"],
            "total_tx_fee": data["total_tx_fee"],
            "txn_pool": data["txn_pool"],
            "miners": data["miners"]
        }

        calls.append(call("""
            SELECT
                SUM(b.txn_count) AS transaction_count,
                COUNT(b.block_hash) AS block_count,
                SUM(b.total_amount) AS total_tx_amount,
                SUM(b.total_fee) AS total_tx_fee
            FROM
                block b
            WHERE
                b.insert_time >= (CURRENT_TIMESTAMP(3) - INTERVAL 1 HOUR)
                AND b.insert_time <= CURRENT_TIMESTAMP(3)"""
                          ))

        calls.append(call("""
            SELECT
                miner,
                COUNT(miner) AS miner_count
            FROM
                (
                    SELECT b.miner
                    FROM block b
                    ORDER BY b.insert_time DESC
                    LIMIT 1000
                ) AS recent_blocks
            GROUP BY
                miner
            ORDER BY
                miner_count DESC
            LIMIT 5"""
                          ))

        calls.append(call("""
            SELECT
                COUNT(txn_hash) AS txn_count
            FROM
                transaction
            WHERE
                status = 'PENDING'"""
                          ))

        mock_execute.assert_has_calls(calls, any_order=True)
