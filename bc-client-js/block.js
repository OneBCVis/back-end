const { putBlock } = require("./utils/stream");

// subscribe to the blockchain client for new blocks

// for each new block
const newBlock = {
    Hash: "BlockHash",
    PreviousBlockHash: "ParentBlockHash",
    Timestamp: "BlockTimestamp",
    Miner: "MinerAddress",
    Transactions: ["TransactionHash1", "TransactionHash2"]
}

// put the block in the kinesis stream
const seqNo = putBlock(newBlock);
