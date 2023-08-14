.load libsqlite_zstd

PRAGMA journal_mode=WAL;
PRAGMA auto_vacuum=full;
PRAGMA busy_timeout=2000;

SELECT
  zstd_enable_transparent('{"table": "transactions", "column": "from", "compression_level": 19, "dict_chooser": "''a''"}'),
  zstd_enable_transparent('{"table": "transactions", "column": "to", "compression_level": 19, "dict_chooser": "''a''"}')
;

SELECT zstd_incremental_maintenance();
