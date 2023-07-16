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

## Example

Download the first 1000 blocks of the Fantom DAG.
Then, extract all transactions and write them to a CSV file.

```bash
mkdir -p var
blockchain.py download fantom 1 1000 var/fantom
blockchain.py transactions-csv 1 1000 var/fantom > var/fantom-txs.csv
```
