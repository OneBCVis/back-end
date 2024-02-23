# test_handler.py

import pytest
from unittest.mock import patch, MagicMock, call

from tests.unit.events.new_txn_block import get_new_txn_block


data = get_new_txn_block()
mock_event = data["event"]
mock_transaction_1 = data["transaction_1"]
mock_transaction_2 = data["transaction_2"]
mock_block_1 = data["block_1"]


@pytest.fixture
def kinesis_event():
    return mock_event


rds_conn_mock = MagicMock()
mock_cursor = MagicMock()
mock_execute = MagicMock()
rds_conn_mock.cursor.return_value = mock_cursor
mock_cursor.execute = mock_execute
mock_cursor.__enter__.return_value.execute = mock_execute
calls = []


def test_lambda_handler(kinesis_event):
    # Mocking pymysql.connect
    with patch("pymysql.connect") as rds_mock:
        rds_mock.return_value = rds_conn_mock

        # Call handler function
        from src.TransactionBlockPublisher.handler import handler
        handler(kinesis_event, None)

        # Assertions
        assert rds_conn_mock.cursor.called
        assert mock_execute.called
        assert rds_conn_mock.commit.called

        assert_transaction_inserted(mock_transaction_1)
        assert_transaction_inserted(mock_transaction_2)
        assert_block_inserted(mock_block_1)
        assert_transaction_update(mock_transaction_1, mock_block_1)
        assert_transaction_update(mock_transaction_2, mock_block_1)

        mock_execute.assert_has_calls(calls, any_order=True)


def assert_transaction_inserted(txn):
    calls.append(call(
        "INSERT INTO transaction (txn_hash, status, amount) VALUES (%s, %s, %s)",
        (
            txn["Hash"],
            txn["Status"],
            txn["Amount"]
        )
    ))

    calls.append(call(
        "INSERT INTO txn_sender (txn_hash, sender_key) VALUES (%s, %s)",
        (
            txn["Hash"],
            txn["Sender"][0]
        )
    ))

    calls.append(call(
        "INSERT INTO txn_receiver (txn_hash, receiver_key) VALUES (%s, %s)",
        (
            txn["Hash"],
            txn["Receiver"][0]
        )
    ))


def assert_block_inserted(block):
    calls.append(call(
        "INSERT INTO block (block_hash, previous_block_hash, timestamp, miner) VALUES (%s, %s, %s, %s)",
        (
            block["Hash"],
            block["PreviousBlockHash"],
            block["Timestamp"],
            block["Miner"]
        )
    ))


def assert_transaction_update(txn, block):
    calls.append(call(
        "INSERT INTO block_txn (block_hash, txn_hash) VALUES (%s, %s)",
        (
            block["Hash"],
            txn["Hash"]
        )
    ))

    calls.append(call(
        "UPDATE transaction SET status = %s WHERE txn_hash = %s",
        (
            "APPROVED",
            txn["Hash"]
        )
    ))