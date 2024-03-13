const { KinesisClient, PutRecordCommand } = require("@aws-sdk/client-kinesis");

const client = new KinesisClient({ region: process.env.KINESIS_STREAM_REGION });

const putTransaction = async (txn) => {
    const input = {
        StreamName: process.env.KINESIS_STREAM_NAME,
        Data: Buffer.from(JSON.stringify({
            type: "TRANSACTION",
            data: txn,
        })),
        PartitionKey: txn.Hash,
        StreamARN: process.env.KINESIS_STREAM_ARN,
    };

    let result = null;
    const command = new PutRecordCommand(input);
    try {
        const response = await client.send(command);
        result = response.SequenceNumber;
        console.log(response);
    } catch (e) {
        console.log(e);
    }

    return result;
}

const putBlock = async (block) => {
    const input = {
        StreamName: process.env.KINESIS_STREAM_NAME,
        Data: Buffer.from(JSON.stringify({
            type: "BLOCK",
            data: block,
        })),
        PartitionKey: block.Hash,
        StreamARN: process.env.KINESIS_STREAM_ARN,
    };

    let result = null;
    const command = new PutRecordCommand(input);
    try {
        const response = await client.send(command);
        result = response.SequenceNumber;
        console.log(response);
    } catch (e) {
        console.log(e);
    }

    return result;
}

module.exports = {
    putTransaction,
    putBlock,
}
