# sqlite examples

## Create tables

```bash
sqlite3 -init create-txs.sql ethereum-txs.sqlite
```

## Import transactions

```bash
sqlite3 -init zstd-txs.sql ethereum-txs.sqlite
```

Import manually with MacOS:

```bash
gzcat ethereum-txs.csv.gz | \
  sqlite3 -init import-txs.sql ethereum-txs.sqlite
```

Import manually with Linux:

```bash
zcat -c ethereum-txs.csv.gz | \
  sqlite3 -init import-txs.sql ethereum-txs.sqlite
```

And then, inside sqlite3, import from stdin:

```sql
.import /dev/stdin transactions
```

## Compress with zstd

First, link `libsqlite_zstd.so` or `libsqlite_zstd.dylib` from `sqlite-zstd/target/release/` to `.`

```bash
sqlite3 -init zstd-txs.sql ethereum-txs.sqlite
```

Or, load zstd manually:

```sql
.load libsqlite_zstd
```
