import json
import gzip
import csv
import io

from lmdbm import Lmdb

class JsonLmdb(Lmdb):
    def _pre_key(self, value):
        return value.encode("utf-8")
    def _post_key(self, value):
        return value.decode("utf-8")
    def _pre_value(self, value):
        return json.dumps(value).encode("utf-8")
    def _post_value(self, value):
        return json.loads(value.decode("utf-8"))

csv_filename = "ethereum-txs.csv.gz"
lmdb_filename = "ethereum.lmdb"

with JsonLmdb.open(lmdb_filename, "c") as db:
    counter = 0
    batch = {}

    # iterate all lines in a csv.gz file
    for row in csv.DictReader(io.TextIOWrapper(gzip.open(csv_filename))):
        # link sender to block
        from_address = row["from"]
        to_address = row["to"]
        block_id = row["block_number"]

        # if the sender is not in the batch, check the db
        if from_address not in batch:
            if from_address in db:
                batch[from_address] = db[from_address]
            else:
                batch[from_address] = {}
        
        if "from" not in batch[from_address]:
            batch[from_address]["from"] = []
        batch[from_address]["from"].append(block_id)

        # if the recipient is not in the batch, check the db
        if to_address not in batch:
            if to_address in db:
                batch[to_address] = db[to_address]
            else:
                batch[to_address] = {}

        if "to" not in batch[to_address]:
            batch[to_address]["to"] = []
        batch[to_address]["to"].append(block_id)

        counter += 1
        if counter % 100000 == 0:
            db.update(batch)
            batch = {}
            print(f"Processed {counter} transactions")
