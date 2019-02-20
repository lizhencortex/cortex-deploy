#!/bin/bash

CUDA90=$(ls /usr/local | grep cuda-9.0)
CUDA92=$(ls /usr/local | grep cuda-9.2)
CUDA10=$(ls /usr/local | grep cuda-10.0)
HAS_CUDA=$CUDA90$CUDA92$CUDA10
MINER_COINBASE='0x92540521018f303c6ae527545a4215dfb0239a16'
CORTEX_BIN_PATH='/opt/cortex/cortex'
CORTEX_KEY_PATH='/opt/cortex/cortex-node-key'

ENODE1='enode://72f70e8e77f68f5526d730f1003e04caa0995eb5c8fb66644da72b23656dc8c16075b0f740d687a3c2aa9d0db1337bf826715c69ae2adb64dc106d3d4165fd79@47.91.91.217:37566'
ENODE2='enode://c5780febab5e5a7bd6387a20a2662df3f1b16a10d93931a40a147e0f6cfd89a576c2e2f758e0e886c3f91a1bc43b3c7fa01af0c8b8ce39c8004c048ca880bccf@47.74.1.234:37566'
ENODE3='enode://9b3b10d4223e010b01411a252312fb69da63b88fd610c07adb5bfa941a8598009a4bb2deeac42c41498acbdaec2196e2cc1fe746286c46f0b5c47d42c5c777b3@47.88.7.24:37566'
ENODE4='enode://0778ac6fe1a572a2f5834452c1d4b6f77b57a2a4baa72e0e2582ad0dbfe88f41e4e66aa020a451a32936a86c29788d257ccaa19f58e5676943595b945e615b9e@139.224.132.6:37566'

if [ -z $HAS_CUDA ]; then
	echo CUDA library not found, stop
	exit 1
fi

if [ -n $CUDA10 ]; then
    CUDA_LIB=$CUDA10
else
    if [ -n $CUDA92 ]; then
        CUDA_LIB=$CUDA92
    else
        CUDA_LIB=$CUDA90
    fi
fi

export PATH=/usr/local/$CUDA_LIB/bin${PATH:+:${PATH}}
export LD_LIBRARY_PATH=/usr/local/$CUDA_LIB/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
$CORTEX_BIN_PATH --port 37566 --rpc --rpccorsdomain '*' --rpcport 30089 --rpcapi web3,eth,ctx,miner,net,txpool --verbosity 4 --storage --cerebro --gcmode archive --mine --miner.coinbase $MINER_COINBASE --miner.threads 0 --miner.gasprice 1 --nodekey $CORTEX_KEY_PATH --miner.extradata cortex-nmg --rpcaddr 0.0.0.0 --bootnodes "$ENODE1,$ENODE2,$ENODE3,$ENODE4"