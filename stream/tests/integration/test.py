# test_handler.py

from unittest import TestCase
import json
import random
import time
import datetime
import boto3
import os
from uuid import uuid4
import requests
import warnings
import pytest

from generate_data import generate_random_txn, generate_random_block


class Test(TestCase):
    aws_region = os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
    kinesis_client = boto3.client("kinesis")

    @classmethod
    def get_stack_name(cls) -> str:
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")
        if not stack_name:
            raise Exception(
                "Cannot find env var AWS_SAM_STACK_NAME. \n"
                "Please setup this environment variable with the stack name where we are running integration tests."
            )
        return stack_name

    def setUp(self) -> None:
        time_zone = os.environ.get("TIME_ZONE") or "UTC"
        os.environ['TZ'] = time_zone
        stack_name = Test.get_stack_name()
        client = boto3.client("cloudformation")
        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name}. \n" f'Please make sure stack with the name "{
                    stack_name}" exists.'
            ) from e
        stack_outputs = response["Stacks"][0]["Outputs"]

        # Kinesis Stream
        kinesis_outputs = [
            output for output in stack_outputs if (output["OutputKey"] == "TransactionBlockStreamArn")]
        self.assertTrue(
            kinesis_outputs, f"Cannot find output TransactionBlockStreamArn in stack {stack_name}")
        self.kinesis_stream_arn = kinesis_outputs[0]["OutputValue"]

        kinesis_outputs = [
            output for output in stack_outputs if (output["OutputKey"] == "TransactionBlockStreamName")]
        self.assertTrue(
            kinesis_outputs, f"Cannot find output TransactionBlockStreamName in stack {stack_name}")
        self.kinesis_stream_name = kinesis_outputs[0]["OutputValue"]

        # API Endpoint
        api_endpoint = [
            output for output in stack_outputs if (output["OutputKey"] == "ApiEndpoint")]
        self.assertTrue(
            api_endpoint, f"Cannot find output ApiEndpoint in stack {stack_name}")
        self.api_endpoint = api_endpoint[0]["OutputValue"]
        self.id_postfix = "_" + str(uuid4())

    def feed_data(self) -> None:
        self.start_time = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f")[:-3]
        self.total_txn_amount = 0
        self.total_txn_fee = 0
        self.txn_pool = 0
        self.miners = {}
        for _ in range(100):
            type = random.randint(0, 20)
            test_event, partition_key = None, None
            if (type != 0):
                test_event, partition_key = generate_random_txn()
                self.txns.append(test_event["data"])
                self.txn_pool += 1
            else:
                test_event, partition_key = generate_random_block()
                self.blocks.append(test_event["data"])
                self.approved_txns += map(
                    lambda txn: txn["Hash"], test_event["data"]["Transactions"].copy())
                self.miners[test_event["data"]["Miner"]] = self.miners.get(
                    test_event["data"]["Miner"], 0) + 1
                self.txn_pool -= len(test_event["data"]["Transactions"])
                for txn in test_event["data"]["Transactions"]:
                    self.total_txn_amount += txn["Amount"]
                    self.total_txn_fee += txn["Fee"]
            self.kinesis_client.put_record(
                StreamName=self.kinesis_stream_name,
                Data=json.dumps(test_event),
                PartitionKey=partition_key,
                StreamARN=self.kinesis_stream_arn
            )
            time.sleep(0.1)
        time.sleep(30)
        self.end_time = datetime.datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S.%f")[:-3]

    def read_stream_data(self) -> None:
        stream_endpoint = self.api_endpoint + \
            f"stream/?start_time={self.start_time}&end_time={self.end_time}"
        response = requests.request(
            method='GET', url=stream_endpoint)
        self.assertEqual(response.status_code, 200)
        response = response.json()

        for orig_txn in self.txns:
            txn = None
            for tx in response["transactions"]:
                if tx["txn_hash"] == orig_txn["Hash"]:
                    txn = tx
                    break
            self.assertIsNotNone(txn)
            self.assertEqual(orig_txn["Hash"], txn["txn_hash"])
            self.assertEqual(orig_txn["Amount"], txn["amount"])
            self.assertEqual(orig_txn["Type"], txn["type"])
            self.assertEqual(orig_txn["Fee"], txn["fee"])

            if (txn["status"] == "APPROVED"):
                self.assertIn(orig_txn["Hash"], self.approved_txns)
            else:
                self.assertEqual(orig_txn["Status"], txn["status"])

        for orig_block in self.blocks:
            block = None
            for blk in response["blocks"]:
                if blk["block_hash"] == orig_block["Hash"]:
                    block = blk
                    break
            self.assertIsNotNone(block)
            self.assertEqual(orig_block["Miner"], block["miner"])
            self.assertEqual(
                str(orig_block["Timestamp"]), str(block["time_stamp"]))
            self.assertEqual(
                orig_block["PreviousBlockHash"], block["previous_block_hash"])
            total_amount = 0
            total_fee = 0
            txn_cnt = len(orig_block["Transactions"])
            for txn in orig_block["Transactions"]:
                self.assertIn(txn["Hash"], block["txn_hashes"])
                total_amount += txn["Amount"]
                total_fee += txn["Fee"]
            self.assertEqual(total_amount, block["total_amount"])
            self.assertEqual(total_fee, block["total_fee"])
            self.assertEqual(txn_cnt, block["txn_cnt"])

    def read_transaction_data(self) -> None:
        txn = random.choice(self.txns)
        txn_endpoint = self.api_endpoint + f"transaction/{txn['Hash']}/"
        response = requests.request(
            method='GET', url=txn_endpoint)
        self.assertEqual(response.status_code, 200)
        response = response.json()

        self.assertEqual(response["txn_hash"], txn["Hash"])
        self.assertEqual(response["amount"], txn["Amount"])
        self.assertEqual(response["type"], txn["Type"])
        self.assertEqual(response["nonce"], txn["Nonce"])
        self.assertEqual(response["fee"], txn["Fee"])

        for (sender, amount) in txn["Sender"]:
            self.assertIn(
                {"sender_key": sender, "amount": amount}, response["senders"])

        for (receiver, amount) in txn["Receiver"]:
            self.assertIn(
                {"receiver_key": receiver, "amount": amount}, response["receivers"])

        if (response["status"] == "APPROVED"):
            self.assertIn(txn["Hash"], self.approved_txns)
        else:
            self.assertEqual(response["status"], txn["Status"])

    def read_block_data(self) -> None:
        block = random.choice(self.blocks)
        total_amount = 0
        total_fee = 0
        for txn in block["Transactions"]:
            total_amount += txn["Amount"]
            total_fee += txn["Fee"]

        block["TotalAmount"] = total_amount
        block["TotalFee"] = total_fee
        block["TxnCount"] = len(block["Transactions"])

        block_endpoint = self.api_endpoint + f"block/{block['Hash']}/"
        response = requests.request(
            method='GET', url=block_endpoint)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.validate_block_data(block, response)

        block_endpoint = self.api_endpoint + \
            f"block/{block['Hash']}/?full=false"
        response = requests.request(
            method='GET', url=block_endpoint)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.validate_block_data(block, response)

        block_endpoint = self.api_endpoint + \
            f"block/{block['Hash']}/?full=true"
        response = requests.request(
            method='GET', url=block_endpoint)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.validate_block_data(block, response, True)

    def validate_block_data(self, block: dict, response: dict, full=False) -> None:
        self.assertEqual(response["block_hash"], block["Hash"])
        self.assertEqual(
            block["previous_block_hash"], block["PreviousBlockHash"])
        self.assertEqual(response["total_amount"], block["TotalAmount"])
        self.assertEqual(response["total_fee"], block["TotalFee"])
        self.assertEqual(response["txn_cnt"], block["TxnCount"])
        self.assertEqual(response["time_stamp"], block["Timestamp"])
        self.assertEqual(response["miner"], block["Miner"])
        self.assertEqual(response["nonce"], block["Nonce"])
        self.assertEqual(response["difficulty"], block["Difficulty"])
        self.assertEqual(response["height"], block["Height"])

        if (full):
            for txn in block["Transactions"]:
                self.assertIn(txn["Hash"], response["txn_hashes"])
            for uncle in block["Uncles"]:
                self.assertIn(uncle, response["uncles"])
            for ocd in block["Sidecar"]:
                self.assertIn(
                    {"id": ocd["Id"], "size": ocd["Size"]}, response["sidecar"])

    def read_stats_data(self) -> None:
        data = '{"start_time": "' + \
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + '"}'
        stats_endpoint = self.api_endpoint + "stats/"
        response = requests.request(
            method='GET', url=stats_endpoint, data=data)
        self.assertEqual(response.status_code, 200)
        response = response.json()

        self.assertEqual(response["transaction_count"],
                         len(self.approved_txns))
        self.assertEqual(response["block_count"], len(self.blocks))
        self.assertEqual(
            response["total_tx_amount"], self.total_txn_amount)
        self.assertEqual(response["total_tx_fee"], self.total_txn_fee)
        self.assertEqual(response["txn_pool"], self.txn_pool)

        miners = response["miners"]
        if (len(self.miners) >= 5):
            self.assertTrue(len(miners) == 5)
        else:
            self.assertTrue(len(miners) == len(self.miners))
        ordered_miners = sorted(
            self.miners.items(), key=lambda x: x[1], reverse=True)
        if (len(ordered_miners) > 5):
            ordered_miners = ordered_miners[:5]
        for miner, count in miners:
            self.assertIn((miner, count), ordered_miners)

    def test(self):
        self.blocks = []
        self.txns = []
        self.approved_txns = []
        self.feed_data()
        self.read_stream_data()
        self.read_transaction_data()
        self.read_stats_data()
