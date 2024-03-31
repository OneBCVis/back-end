import random


txn_pool = []
prev_block_hash = "0x" + ''.join(random.choices('0123456789abcdef', k=32))
miners = ["0x" + ''.join(random.choices('0123456789abcdef', k=32))
          for _ in range(10)]


def generate_random_txn():
    global txn_pool
    txn = {}
    txn["Hash"] = "0x" + ''.join(random.choices('0123456789abcdef', k=32))
    txn["Status"] = 'PENDING'
    txn["Amount"] = random.randint(1, 99)
    txn["Type"] = random.choice([1, 2, 3])
    txn["Nonce"] = random.randint(0, 999999)
    txn["Fee"] = random.randint(1, 9)
    txn["Sender"] = [
        ["0x" + ''.join(random.choices('0123456789abcdef', k=32)), txn["Amount"]]]
    txn["Receiver"] = [
        ["0x" + ''.join(random.choices('0123456789abcdef', k=32)), txn["Amount"]]]
    txn_pool.append(txn)
    message = {}
    message["type"] = "TRANSACTION"
    message["data"] = txn
    return message, txn["Hash"]


def generate_random_block():
    global txn_pool, prev_block_hash, miners
    block = {}
    block["Hash"] = "0x" + ''.join(random.choices('0123456789abcdef', k=32))
    block["PreviousBlockHash"] = prev_block_hash
    block["Height"] = random.randint(1, 100)
    block["Nonce"] = random.randint(0, 999999)
    block["Difficulty"] = random.randint(1, 100)
    block["Miner"] = random.choice(miners)
    block["Timestamp"] = random.randint(1000000000, 2000000000)
    block["Transactions"] = []
    for _ in range(random.randint(0, len(txn_pool))):
        txn = random.choice(txn_pool)
        txn_pool.remove(txn)
        txn["Status"] = 'APPROVED'
        block["Transactions"].append(txn)
    block["Uncles"] = []
    block["Sidecar"] = []
    if (len(block["Transactions"]) > 0):
        for _ in range(random.randint(0, 3)):
            off_chain_data = {}
            off_chain_data["ID"] = "0x" + \
                ''.join(random.choices('0123456789abcdef', k=32))
            off_chain_data["Size"] = random.randint(1024, 2048)
            off_chain_data["TransactionID"] = random.choice(
                block["Transactions"])["Hash"]
            block["Sidecar"].append(off_chain_data)
    block["OffChainDataSizes"] = [random.randint(1024, 2048) for _ in range(2)]
    prev_block_hash = block["Hash"]
    message = {}
    message["type"] = "BLOCK"
    message["data"] = block
    return message, block["Hash"]
