.separator ,
.mode csv data

CREATE TABLE transactions (
    "block_number" INTEGER,
    "tx_hash" TEXT PRIMARY KEY,
    "method" TEXT,
    "from" TEXT,
    "to" TEXT,
    "quantity" INTEGER
);

-- pragma journal_mode=WAL;
-- pragma auto_vacuum=full;
-- pragma busy_timeout=2000;
-- PRAGMA hard_heap_limit=191000;
-- .load libsqlite_zstd.so;
-- SELECT
--   zstd_enable_transparent('{"table": "transactions", "column": "tx_hash", "compression_level": 19, "dict_chooser": "''a''"}');

.import /dev/stdin transactions

CREATE INDEX txs_from ON transactions("from");
CREATE INDEX txs_to ON transactions("to");
CREATE INDEX txs_method ON transactions("method");

-- SELECT zstd_incremental_maintenance();
