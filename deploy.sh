#!/bin/bash

clean() {
    DPLOY_PATH="/opt/cortex"
    echo 'Try to stop existing cortexnode'
    supervisorctl stop cortexnode
    echo 'Try to stop existing monitor service'
    service cortex-monitor.sh stop
    echo 'Try to remove existing deployment directory'
    rm -rf $DPLOY_PATH
}

COMMAND=""

deploy() {
    local HAS_NVIDIA_DRIVER=$(which nvidia-smi)
    if [ -z $HAS_NVIDIA_DRIVER ]; then
        echo NVIDIA driver not found, stop
        exit 1
    else
        echo NVIDIA driver detected
    fi

    local HAS_SUPERVISORD=$(which supervisord)
    if [ -z $HAS_SUPERVISORD ]; then
        echo Supervisor not found, stop
        exit 1
    else
        echo Supervisor detected
    fi
    clean

    local CUDA90=$(ls /usr/local | grep cuda-9.0)
    local CUDA92=$(ls /usr/local | grep cuda-9.2)
    local CUDA10=$(ls /usr/local | grep cuda-10.0)
    local CUDA101=$(ls /usr/local | grep cuda-10.1)
    local HAS_CUDA=$CUDA90$CUDA92$CUDA10$CUDA101
    DPLOY_PATH="/opt/cortex"

    if [ -z $HAS_CUDA ]; then
        echo CUDA library not found, stop
        exit 1
    fi

    echo CUDA detected
    if [ -n "$1" ]; then
        DPLOY_PATH="$1"
    fi

    rm -rf $DPLOY_PATH
    mkdir -p $DPLOY_PATH
    chmod 777 $DPLOY_PATH -R
    mkdir -p $DPLOY_PATH/logs
    wget https://codeload.github.com/lizhencortex/cortex-deploy/zip/dev -O cortex-package.zip
    local DOWNLOAD_STATUS=$(ls | grep cortex-package.zip)
    if [ -z $DOWNLOAD_STATUS ]; then
        echo download failed
        exit 1
    fi
    wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/master/cortex-core/cortex_v1.0.0-stable.zip
    local DOWNLOAD_STATUS=$(ls | grep cortex-v1.0.0-stable.zip)
    if [ -z $DOWNLOAD_STATUS ]; then
        echo download failed
        exit 1
    fi

    unzip cortex_v1.0.0-stable.zip -d cortex-bin-tmp
    unzip cortex-package.zip -d cortex-deploy-tmp
    chmod +x ./cortex-package-tmp/cortex-monitor.sh
    mv ./cortex-package-tmp/cortex-monitor.sh /etc/init.d/cortex-monitor.sh
    mv ./cortex-package-tmp/cortexnode.conf /etc/supervisor/conf.d/cortexnode.conf
    echo $(uuidgen) > /opt/cortex/uuid

    mv ./cortex-package-tmp/cortex-monitor.py $DPLOY_PATH/
    mv ./cortex-package-tmp/cortex.sh $DPLOY_PATH/
    mv ./cortex-bin-tmp/* $DPLOY_PATH/
    chmod +x $DPLOY_PATH/cortex
    chmod +x $DPLOY_PATH/cortex.sh

    update-rc.d cortex-monitor.sh defaults

    supervisorctl reload
    sleep 5
    service cortex-monitor.sh start

    rm cortex-package.zip
    rm -r ./cortex-package-tmp
    rm -r ./cortex-bin-tmp

    echo deploy finish
}

helpdoc() {
    echo "Cortex full node deployment tool (version 0.1)"
    echo "Usage: sudo $0 [options] command"

    echo "Most used commands:"
    echo "  deploy - download and deploy cortex fullnode"
    echo "  clean - clean the current cortex environment"
}

if [ $UID -ne 0 ]; then
    echo "Superuser privileges are required to run this script."
    echo "=================================================================="
    helpdoc
    exit 1
fi

case "$1" in

    'deploy')
        deploy
        ;;

    'install')
        deploy
        ;;

    'clean')
        clean
        echo 'Try to remove existing cortex chain data'
        rm -rf /root/.cortex
        rm -rf $HOME/.cortex
        ;;

    *)
        helpdoc
        exit 1
        ;;
esac

exit 0
