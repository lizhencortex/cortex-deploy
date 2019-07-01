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
    local HAS_SUPERVISORD=$(which supervisord)
    if [ -z $HAS_SUPERVISORD ]; then
        echo Supervisor not found, stop
        exit 1
    else
        echo Supervisor detected
    fi
    clean

    DPLOY_PATH="/opt/cortex"
    if [ -n "$1" ]; then
        DPLOY_PATH="$1"
    fi

    rm -rf $DPLOY_PATH
    mkdir -p $DPLOY_PATH
    chmod 777 $DPLOY_PATH -R
    mkdir -p $DPLOY_PATH/logs
    rm cortex-package.zip >/dev/null 2>&1
    rm -rf cortex-deploy-dev >/dev/null 2>&1
    rm cortex-stable.zip  >/dev/null 2>&1
    rm -rf cortex >/dev/null 2>&1
    wget https://codeload.github.com/lizhencortex/cortex-deploy/zip/dev -O cortex-package.zip
    local DOWNLOAD_STATUS=$(ls | grep cortex-package.zip)
    if [ -z $DOWNLOAD_STATUS ]; then
        echo download failed
        exit 1
    fi
#    wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/master/cortex-core/cortex_v1.0.0_3610c75d-stable.zip -O cortex-stable.zip
#    local DOWNLOAD_STATUS=$(ls | grep cortex-stable.zip)
#    if [ -z $DOWNLOAD_STATUS ]; then
#        echo download failed
#        exit 1
#    fi

    unzip cortex-package.zip
    unzip cortex-deploy-dev/cortex.zip
    chmod +x ./cortex-deploy-dev/cortex-monitor.sh
    mv ./cortex-deploy-dev/cortex-monitor.sh /etc/init.d/cortex-monitor.sh
    mv ./cortex-deploy-dev/cortexnode.conf /etc/supervisor/conf.d/cortexnode.conf
    echo $(uuidgen) > /opt/cortex/uuid

    mv ./cortex-deploy-dev/cortex-monitor.py $DPLOY_PATH/
    mv ./cortex-deploy-dev/cortex.sh $DPLOY_PATH/
    mv ./cortex/* $DPLOY_PATH/
    chmod +x $DPLOY_PATH/cortex
    chmod +x $DPLOY_PATH/cortex.sh

    update-rc.d cortex-monitor.sh defaults

    supervisorctl update cortexnode
    supervisorctl start cortexnode
    sleep 5
    service cortex-monitor.sh start

    rm cortex-package.zip
    rm -r ./cortex-deploy-dev
    rm -r ./cortex

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
