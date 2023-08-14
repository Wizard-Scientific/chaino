CREATE TABLE IF NOT EXISTS transactions (
    "block_number" INTEGER,
    "tx_hash" TEXT PRIMARY KEY,
    "method" TEXT,
    "from" TEXT,
    "to" TEXT,
    "quantity" INTEGER
);
