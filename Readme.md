# Chaino

Chaino is a blockchain research tool to rapidly:

- download blocks from a blockchain
- issue calls against smart contracts

Chaino can use multiple RPCs in parallel, each with multiple threads.
Chaino attempts to automatically maximize its speed without abusing the RPC.

Blocks are stored as web3.py objects inside Python pickle files.
The block files are archived with NestedFilestore, which can manage millions of files on a filesystem.

## Installation

```bash
pip install 'git+https://github.com/0xidm/chaino'
```

## Python example: Block download

Download the first 1000 blocks of the Fantom DAG.

```python
from web3 import Web3, HTTPProvider
from chaino.scheduler.block import BlockScheduler
from chaino.rpc import RPC

scheduler = BlockScheduler(filestore_path="/tmp/example")
scheduler.add_rpc(RPC(w3=Web3(HTTPProvider("https://rpc.ftm.tools"))))
for block_number in range(1, 1000):
    scheduler.add_task(block_number=block_number)
scheduler.start()
```

Results will be available as a NestedFilestore in `/tmp/example`.

## Python example: Calling contract functions

Get ERC-20 balances for a list of addresses on Fantom.

```python
from chaino.scheduler.call import CallScheduler, parse_address
from chaino.rpc import RPC

result = CallScheduler.map_call(
    rpc=RPC(url="https://rpc.ftm.tools"),
    contract_address="0x21Ada0D2aC28C3A5Fa3cD2eE30882dA8812279B6",
    function_signature="balanceOf(address)(uint256)",
    inputs=[
        ["0x5aa1039D09330DF607F88e72bb9C1E0F66C96AA0"],
        ["0x18Bf8D51f7695AA3E63fEA9E99416530c1420511"],
    ]
)
[(parse_address(key), value) for key, value in result.items()]
```

which produces these results:

```python
[('0x5aa1039D09330DF607F88e72bb9C1E0F66C96AA0', 5925106268789833088835427),
 ('0x18Bf8D51f7695AA3E63fEA9E99416530c1420511', 2765360879676247594525586)]
```

## Command Line Example

Download the first 1000 blocks of the Fantom DAG.
Then, extract all transactions and write them to a CSV file.

```bash
mkdir -p var
blockchain.py download fantom 1 1000 var/fantom
blockchain.py transactions-csv 1 1000 var/fantom > var/fantom-txs.csv
```
