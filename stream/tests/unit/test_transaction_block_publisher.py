# test_handler.py

import pytest
import json
from unittest.mock import patch, MagicMock, call

from tests.unit.events.new_txn_block import get_new_txn_block


data = get_new_txn_block()
mock_event = data["event"]
mock_transaction_1 = data["transaction_1"]
mock_transaction_2 = data["transaction_2"]
duplicate_transaction = data["duplicate_transaction"]
mock_unpublished_transaction = data["unpublished_transaction"]
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
mock_client = MagicMock()
mock_client.get_secret_value.return_value = {
    "SecretString": '{"username": "XXXX", "password": "XXXX"}'
}
mock_cursor.__enter__.return_value.fetchone.side_effect = [
    (0,), (0,), (2,), (1,), (1,), (0,)]
calls = []


def test_lambda_handler(kinesis_event):
    # Mocking pymysql.connect
    with patch("pymysql.connect") as rds_mock, patch("boto3.client") as boto3_mock:
        rds_mock.return_value = rds_conn_mock
        boto3_mock.return_value = mock_client

        # Call handler function
        from src.TransactionBlockPublisher.handler import handler
        handler(kinesis_event, None)

        # Assertions
        assert rds_conn_mock.cursor.called
        assert mock_execute.called
        assert rds_conn_mock.commit.called

        assert_transaction_inserted(mock_transaction_1)
        assert_transaction_inserted(mock_transaction_2)
        assert_transaction_inserted(duplicate_transaction)
        assert_block_inserted(mock_block_1)
        for txn in mock_block_1["Transactions"]:
            assert_transaction_update(txn, mock_block_1)

        mock_execute.assert_has_calls(calls, any_order=True)


def assert_transaction_inserted(txn, is_full=False):
    calls.append(call(
        "call insert_transaction(%s, %s, %s, %s, %s, %s, %s, %s, %s, @result)",
        (
            txn["Hash"],
            txn["Status"],
            txn["Amount"],
            txn["Type"],
            txn["Nonce"],
            txn["Fee"],
            json.dumps(txn["Sender"]),
            json.dumps(txn["Receiver"]),
            is_full
        )
    ))

    calls.append(call("SELECT @result AS result"))


def assert_block_inserted(block):
    calls.append(call(
        """INSERT INTO block
                                (block_hash, previous_block_hash, height, nonce, difficulty, miner, time_stamp)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (
            block["Hash"],
            block["PreviousBlockHash"],
            block["Height"],
            block["Nonce"],
            block["Difficulty"],
            block["Miner"],
            block["Timestamp"]
        )
    ))

    for uncle in block["Uncles"]:
        calls.append(call(
            "INSERT INTO uncle (uncle_hash, block_hash) VALUES (%s, %s)",
            (
                uncle,
                block["Hash"]
            )
        ))

    for offChainData in block["Sidecar"]:
        calls.append(call(
            """INSERT INTO off_chain_data
                                        (block_hash, id, txn_id, size)
                                        VALUES (%s, %s, %s, %s)""",
            (
                block["Hash"],
                offChainData["ID"],
                offChainData["TransactionID"],
                offChainData["Size"]
            )
        ))


def assert_transaction_update(txn, block):
    assert_transaction_inserted(txn, is_full=True)

    calls.append(call(
        "INSERT INTO block_txn (block_hash, txn_hash) VALUES (%s, %s)",
        (
            block["Hash"],
            txn["Hash"]
        )
    ))
