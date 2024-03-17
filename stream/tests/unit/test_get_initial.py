# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.get_initial import get_initial


data = get_initial()
mock_event = data["event"]
mock_data = data["data"]


rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.fetchall.side_effect = [[(
    json.dumps(mock_data["txn_types"]),
)], [(mock_data["txn_pool"],)]]
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}
calls = []


def test_lambda_handler():
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        from src.GetInitial.handler import handler, headers
        response = handler(mock_event, None)

        assert rds_conn_mock.cursor.called
        assert mock_execute.call_count == 2
        calls.append(call("""
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'type', type,
                    'name', name
                )
            )
            FROM txn_type"""))
        calls.append(call("""
            SELECT COUNT(txn_hash)
            FROM transaction
            WHERE status = 'pending'"""))
        mock_execute.assert_has_calls(calls, any_order=True)
        assert mock_cursor.fetchall.call_count == 2

        assert response["statusCode"] == 200
        assert response["headers"] == headers
        assert json.loads(response["body"]) == mock_data
