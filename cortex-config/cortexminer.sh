#!/bin/sh

CUDA90=$(ls /usr/local | grep cuda-9.0)
CUDA92=$(ls /usr/local | grep cuda-9.2)
CUDA10=$(ls /usr/local | grep cuda-10.0)
HAS_CUDA=$CUDA90$CUDA92$CUDA10
MINER_COINBASE='0x92540521018f303c6ae527545a4215dfb0239a16'
CORTEX_MINER_PATH='/opt/cortex/cuda_miner'
MINERPOOL_ADDR='localhost:8009'

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
$CORTEX_MINER_PATH --verbosity 5 --pool_uri $MINERPOOL_ADDR
