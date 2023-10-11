.load ./libsqlite_zstd
.separator ,
.mode csv

PRAGMA journal_mode=WAL;
PRAGMA auto_vacuum=full;
PRAGMA busy_timeout=2000;
PRAGMA temp_store_directory=".";

-- denormalize the transaction from field

CREATE TABLE IF NOT EXISTS tx_from (
    "txid" INTEGER PRIMARY KEY,
    "from" INTEGER
);
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[4];}'" tx_from
CREATE INDEX idx_txs_from ON tx_from("from");
SELECT zstd_enable_transparent('{"table": "tx_from", "column": "from", "compression_level": 10, "dict_chooser": "''a''"}') from tx_from;
SELECT zstd_incremental_maintenance(null, 0.5);
VACUUM;

-- denormalize the transaction to field

CREATE TABLE IF NOT EXISTS tx_to (
    "id" INTEGER PRIMARY KEY,
    "to" TEXT
);
SELECT zstd_enable_transparent('{"table": "tx_to", "column": "to", "compression_level": 10, "dict_chooser": "''a''"}') from tx_to;
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[5];}'" tx_to
SELECT zstd_incremental_maintenance(10, 0.5);
VACUUM;
CREATE INDEX idx_txs_to ON tx_to("to");

-- denormalize the transaction hash field

CREATE TABLE IF NOT EXISTS tx_hash (
    "id" INTEGER PRIMARY KEY,
    "hash" TEXT,
);
SELECT zstd_enable_transparent('{"table": "tx_hash", "column": "hash", "compression_level": 10, "dict_chooser": "''a''"}') from tx_hash;
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[2];}'" tx_hash
SELECT zstd_incremental_maintenance(10, 0.5);
VACUUM;
CREATE INDEX idx_txs_hash ON tx_hash("hash");

-- denormalize the transaction block number field

CREATE TABLE IF NOT EXISTS tx_block (
    "id" INTEGER PRIMARY KEY,
    "block_number" INTEGER
);
SELECT zstd_enable_transparent('{"table": "tx_block", "column": "block_number", "compression_level": 10, "dict_chooser": "''a''"}') from tx_block;
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[1];}'" tx_block
SELECT zstd_incremental_maintenance(10, 0.5);
VACUUM;
CREATE INDEX idx_txs_block ON tx_block("block_number");

-- denormalize the transaction method field

CREATE TABLE IF NOT EXISTS tx_method (
    "id" INTEGER PRIMARY KEY,
    "method" TEXT
);
SELECT zstd_enable_transparent('{"table": "tx_method", "column": "method", "compression_level": 10, "dict_chooser": "''a''"}') from tx_method;
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[3];}'" tx_method
SELECT zstd_incremental_maintenance(10, 0.5);
VACUUM;
CREATE INDEX idx_txs_method ON tx_method("method");

-- denormalize the transaction value field

CREATE TABLE IF NOT EXISTS tx_value (
    "id" INTEGER PRIMARY KEY,
    "value" TEXT
);
SELECT zstd_enable_transparent('{"table": "tx_value", "column": "value", "compression_level": 10, "dict_chooser": "''a''"}') from tx_value;
.import "| zcat -c ethereum-txs.csv.gz | tail -n +2 | awk '{OFS=\",\"; split($0, tx, \",\"); print NR, tx[6];}'" tx_value
SELECT zstd_incremental_maintenance(10, 0.5);
VACUUM;
CREATE INDEX idx_txs_value ON tx_value("value");
