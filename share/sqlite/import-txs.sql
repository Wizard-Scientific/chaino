.separator ,
.mode csv
.import '| zcat -c ethereum-txs.csv.gz | tail -n +2' transactions

CREATE INDEX txs_from ON transactions("from");
CREATE INDEX txs_to ON transactions("to");
CREATE INDEX txs_method ON transactions("method");
