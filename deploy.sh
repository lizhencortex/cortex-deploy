#!/bin/bash

if [ $UID -ne 0 ]; then
    echo "Superuser privileges are required to run this script."
    echo "e.g. \"sudo $0\""
    exit 1
fi

mkdir cortex-install
cd cortex-install

HAS_NVIDIA_DRIVER=$(which nvidia-smi)
if [ -z $HAS_NVIDIA_DRIVER ]; then
	echo NVIDIA driver not found, stop
	exit 1
else
    echo NVIDIA driver detected
fi

HAS_SUPERVISORD=$(which supervisord)
if [ -z $HAS_SUPERVISORD ]; then
	echo Supervisor not found, stop
	exit 1
else
    echo Supervisor detected
fi

CUDA90=$(ls /usr/local | grep cuda-9.0)
CUDA92=$(ls /usr/local | grep cuda-9.2)
CUDA10=$(ls /usr/local | grep cuda-10.0)
HAS_CUDA=$CUDA90$CUDA92$CUDA10
DPLOY_PATH="/opt/cortex"

if [ -z $HAS_CUDA ]; then
	echo CUDA library not found, stop
	exit 1
fi

if [ -n $CUDA10 ]; then
    echo CUDA10.0 detected
    wget https://raw.githubusercontent.com/lizhencortex/MonitorServer/master/static/cortex-cuda10.0
    DOWNLOAD_STATUS=$(ls | grep cortex-cuda10.0)
    if [ -z $DOWNLOAD_STATUS ]; then
        echo download failed
        exit 1
    fi
    mv cortex-cuda10.0 cortex
#    wget https://raw.githubusercontent.com/lizhencortex/MonitorServer/master/static/miner-cuda10.0
#    mv miner-cuda10.0 cuda_miner
else
    if [ -n $CUDA92 ]; then
        echo CUDA9.2 detected
        wget https://raw.githubusercontent.com/lizhencortex/MonitorServer/master/static/cortex-cuda9.2
        DOWNLOAD_STATUS=$(ls | grep cortex-cuda9.2)
        if [ -z $DOWNLOAD_STATUS ]; then
            echo download failed
            exit 1
        fi
        mv cortex-cuda9.2 cortex
    else
        echo CUDA9.0 detected
        wget https://raw.githubusercontent.com/lizhencortex/MonitorServer/master/static/cortex-cuda9.0
        DOWNLOAD_STATUS=$(ls | grep cortex-cuda9.0)
        if [ -z $DOWNLOAD_STATUS ]; then
            echo download failed
            exit 1
        fi
        mv cortex-cuda9.0 cortex
    fi
fi

if [ -n "$1" ]; then
    DPLOY_PATH="$1" 
fi

rm -rf $DPLOY_PATH
mkdir -p $DPLOY_PATH
mkdir -p $DPLOY_PATH/logs
wget https://raw.githubusercontent.com/lizhencortex/MonitorServer/master/static/cortex-package.tar.gz
DOWNLOAD_STATUS=$(ls | grep cortex-package.tar.gz)
if [ -z $DOWNLOAD_STATUS ]; then
    echo download failed
    exit 1
fi
tar zxvf cortex-package.tar.gz
mv -r ./cortex-package/script/* $DPLOY_PATH/
mv cortex $DPLOY_PATH/
#mv cuda_miner $DPLOY_PATH/
chmod +x ./cortex-package/service/cortex-monitor.sh
mv ./cortex-package/service/cortex-monitor.sh /etc/init.d/
update-rc.d cortex-monitor.sh defaults
mv ./cortex-package/supervisor-config/cortexnode.conf /etc/supervisor/conf.d/

supervisorctl reload
sleep 5
service cortex-monitor.sh start

rm cortex-package.tar.gz
rm -r ./cortex-package

echo deploy finish
