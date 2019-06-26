#!/bin/bash

CUDA92=$(ls /usr/local | grep cuda-9.2)
CUDA10=$(ls /usr/local | grep cuda-10.0)
CUDA101=$(ls /usr/local | grep cuda-10.1)
CUDA102=$(ls /usr/local | grep cuda-10.2)
HAS_CUDA=$CUDA92$CUDA10$CUDA101$CUDA102
CORTEX_BIN_PATH=/opt/cortex/cortex
MINER_COINBASE='0xc0d86d03f451e38c2ee0fa0daf5c8d6e2d1243d2'
DATA_DIR='data'
RPC_API='personal,web3,ctxc,miner,net,txpool,admin'

if [ -z $HAS_CUDA ]; then
	echo CUDA library not found, stop
	exit 1
fi

export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=$(pwd):/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}

$CORTEX_BIN_PATH --port 30088 \
    --rpc --rpcvhosts '*' --rpccorsdomain '*' --rpcport 30089 --rpcapi $RPC_API --rpcaddr "127.0.0.1" \
    --verbosity 3 \
    --mine --miner.threads=0 --miner.cuda --miner.devices=0 \
    --miner.coinbase=$MINER_COINBASE --datadir=$DATA_DIR
