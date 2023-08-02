#!/bin/bash

function export_group() {
    local START_BLOCK=$1
    local END_BLOCK=$2
    local GROUP=$3

    ./bin/blockchain.py transactions-csv \
        $BLOCKCHAIN_PATH/ethereum ${START_BLOCK} ${END_BLOCK} | gzip > \
        $BLOCKCHAIN_PATH/ethereum-txs-${GROUP}.csv.gz
}

export_group        0   999999 000
export_group  1000000  1999999 001
export_group  2000000  2999999 002
export_group  3000000  3999999 003
export_group  4000000  4999999 004
export_group  5000000  5999999 005
export_group  6000000  6999999 006
export_group  7000000  7999999 007
export_group  8000000  8999999 008
export_group  9000000  9999999 009
export_group 10000000 10999999 010
export_group 11000000 11999999 011
export_group 12000000 12999999 012
export_group 13000000 13999999 013
export_group 14000000 14999999 014
export_group 15000000 15999999 015
export_group 16000000 16999999 016
export_group 17000000 17999999 017
