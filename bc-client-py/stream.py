import boto3
import botocore
import os
import json
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class KinesisStream:
    def __init__(self):
        self.client = boto3.client(service_name='kinesis', region_name=os.environ['KINESIS_STREAM_REGION'])
        self.name = os.environ['KINESIS_STREAM_NAME']
        self.arn = os.environ['KINESIS_STREAM_ARN']
        self.stream_exists_waiter = self.client.get_waiter("stream_exists")


    def __put_record(self, data, partition_key):
        try:
            response = self.kinesis_client.put_record(
                StreamName=self.name,
                Data=json.dumps(data),
                PartitionKey=partition_key,
                StreamARN=self.arn
            )
            logger.info("Put record in stream %s.", self.name)
            logger.debug("Response: %s", response)
        except botocore.exceptions.ClientError as e:
            logger.exception("Couldn't put record in stream %s.", self.name)
            logger.debug("Error: %s", e)
        else:
            return response['SequenceNumber']
        
    
    def put_transaction(self, transaction):
        message = {
            'type': 'TRANSACTION',
            'data': transaction
        }
        self.__put_record(message, transaction['Hash'])


    def put_block(self, block):
        message = {
            'type': 'BLOCK',
            'data': block
        }
        self.__put_record(message, block['Hash'])
