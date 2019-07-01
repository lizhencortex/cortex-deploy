#!/bin/bash

CORTEX_BIN_PATH=/opt/cortex/cortex
MINER_COINBASE='0xc0d86d03f451e38c2ee0fa0daf5c8d6e2d1243d2'
DATA_DIR='data'
RPC_API='personal,web3,ctxc,miner,net,txpool,admin'

export LD_LIBRARY_PATH=$(pwd):${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

$CORTEX_BIN_PATH --port 30088 \
    --rpc --rpcvhosts '*' --rpccorsdomain '*' --rpcport 30089 --rpcapi $RPC_API --rpcaddr "127.0.0.1" \
    --verbosity 3 \
    --miner.threads=0 \
    --miner.coinbase=$MINER_COINBASE --datadir=$DATA_DIR
