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

Or just initialize the library.

```bash
sqlite3 -cmd '.load libsqlite_zstd' tmp.sqlite
```

Or, load zstd manually:

```sql
.load libsqlite_zstd
```

## Compiling

### Build sqlite3

https://github.com/sqlite/sqlite

```bash
docker pull gcc:11-bullseye
git clone https://github.com/sqlite/sqlite
docker run -it --rm --name builder -v $PWD/sqlite:/mnt/sqlite gcc:11-bullseye \
  /bin/bash -c 'apt update; apt install -y tcl; cd /mnt/sqlite; mkdir -p bld; cd bld; ../configure; make -j3'
mkdir -p ~/.local/bin && cp ./sqlite/bld/sqlite3 ~/.local/bin
```

## Build sqlite zstd extension

https://github.com/phiresky/sqlite-zstd

```bash
docker pull rust
git clone https://github.com/phiresky/sqlite-zstd
docker run -it --rm --name builder -v $PWD/sqlite-zstd:/mnt/sqlite-zstd rust \
  /bin/bash -c 'cd /mnt/sqlite-zstd && cargo build --release --features build_extension'
mkdir -p ~/.local/lib && cp ./sqlite-zstd/target/release/libsqlite_zstd.so ~/.local/lib
sqlite3 /tmp/test.sqlite
```

Now use this inside sqlite3: `.load $HOME/.local/lib/libsqlite_zstd`
