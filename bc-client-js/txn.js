const { putTransaction } = require("./utils/stream");

// subscribe to the blockchain client for new transactions

// for each new transaction
const pendingTX = {
    Hash: "TransactionHash",
    Sender: ["fromAddress1", "fromAddress2"],
    Receiver: ["toAddress1", "toAddress2"],
    Amount: 0,
    Status: "PENDING"
}

// put the transaction in the kinesis stream
const seqNo = putTransaction(pendingTX);
