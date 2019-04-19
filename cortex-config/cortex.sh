#!/bin/bash

CUDA=$(ls /usr/local | grep CUDA_VERSION)

MINER_COINBASE='0x92540521018f303c6ae527545a4215dfb0239a16'
CORTEX_BIN_PATH='/opt/cortex/cortex'
CORTEX_KEY_PATH='/opt/cortex/cortex-node-key'

CUDA_LIB=CUDA_VERSION

export PATH=/usr/local/$CUDA_LIB/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/$CUDA_LIB/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
$CORTEX_BIN_PATH --port 37566 --rpc --rpccorsdomain '*' --rpcport 30089 --rpcapi admin,web3,eth,ctx,miner,net,txpool --verbosity 4 --storage --cerebro --gcmode archive
