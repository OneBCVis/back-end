# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_txn import get_txn


data = get_txn()
mock_event = data["event"]
mock_txn = data["txn"]
mock_txn_body = data["txn_body"]


rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.return_value = [(
    mock_txn_body["txn_hash"],
    mock_txn_body["status"],
    mock_txn_body["amount"],
    mock_txn_body["type"],
    mock_txn_body["nonce"],
    mock_txn_body["fee"],
    mock_txn_body["senders"],
    mock_txn_body["receivers"]
)]
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}

mock_txn_body_copy = mock_txn_body.copy()
mock_txn_body_copy["senders"] = json.loads(mock_txn_body_copy["senders"])
mock_txn_body_copy["receivers"] = json.loads(mock_txn_body_copy["receivers"])


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        from src.GetTransaction.handler import handler, headers
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.called
        assert mock_execute.call_args[0][0] == """
            SELECT
                t.txn_hash,
                t.status,
                t.amount,
                t.type,
                t.nonce,
                t.fee,
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'sender_key',   sender_key,
                            'amount',       amount
                        )
                    )
                    FROM txn_sender
                    WHERE txn_hash = t.txn_hash
                ) AS senders,
                (
                    SELECT JSON_ARRAYAGG(
                        JSON_OBJECT(
                            'receiver_key', receiver_key,
                            'amount',       amount
                        )
                    )
                    FROM txn_receiver
                    WHERE txn_hash = t.txn_hash
                ) AS receivers
            FROM
                transaction t
            WHERE
                t.txn_hash = %s"""
        assert mock_execute.call_args[0][1] == mock_txn["txn_hash"]
        assert mock_cursor.fetchall.called

        assert response["statusCode"] == 200
        assert response["headers"] == headers
        assert json.loads(response["body"]) == mock_txn_body_copy
