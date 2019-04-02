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
    clean

    CUDA90=$(ls /usr/local | grep cuda-9.0)
    CUDA92=$(ls /usr/local | grep cuda-9.2)
    CUDA10=$(ls /usr/local | grep cuda-10.0)
    CUDA101=$(ls /usr/local | grep cuda-10.1)
    HAS_CUDA=$CUDA90$CUDA92$CUDA10$CUDA101
    DPLOY_PATH="/opt/cortex"

    if [ -z $HAS_CUDA ]; then
        echo CUDA library not found, stop
        exit 1
    fi

    if [ -n $CUDA101 ]; then
        echo CUDA10.1 detected
        if [ "$1" != "install" ]; then
            wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/dev/cortex-core/bin/cortex-cuda10.1 -O cortex-cuda10.1
        fi
        DOWNLOAD_STATUS=$(ls | grep cortex-cuda10.1)
        if [ -z $DOWNLOAD_STATUS ]; then
            echo download failed
            exit 1
        fi
        mv cortex-cuda10.1 cortex
    else
        if [ -n $CUDA10 ]; then
            echo CUDA10.0 detected
            if [ "$1" != "install" ]; then
                wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/dev/cortex-core/bin/cortex-cuda10.0 -O cortex-cuda10.0
            fi
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
                if [ "$1" != "install" ]; then
                    wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/dev/cortex-core/bin/cortex-cuda9.2 -O cortex-cuda9.2
                fi
                DOWNLOAD_STATUS=$(ls | grep cortex-cuda9.2)
                if [ -z $DOWNLOAD_STATUS ]; then
                    echo download failed
                    exit 1
                fi
                mv cortex-cuda9.2 cortex
            else
                echo CUDA9.0 detected
                if [ "$1" != "install" ]; then
                    wget https://raw.githubusercontent.com/CortexFoundation/Cortex_Release/dev/cortex-core/bin/cortex-cuda9.0 -O cortex-cuda9.0
                fi
                DOWNLOAD_STATUS=$(ls | grep cortex-cuda9.0)
                if [ -z $DOWNLOAD_STATUS ]; then
                    echo download failed
                    exit 1
                fi
                mv cortex-cuda9.0 cortex
            fi
        fi
    fi
    chmod +x cortex

    if [ -n "$1" ]; then
        DPLOY_PATH="$1" 
    fi

    rm -rf $DPLOY_PATH
    mkdir -p $DPLOY_PATH
    chmod 777 $DPLOY_PATH -R
    mkdir -p $DPLOY_PATH/logs
    wget https://codeload.github.com/lizhencortex/cortex-deploy/zip/master -O cortex-package.zip
    DOWNLOAD_STATUS=$(ls | grep cortex-package.zip)
    if [ -z $DOWNLOAD_STATUS ]; then
        echo download failed
        exit 1
    fi

    unzip cortex-package.zip
    mv cortex-deploy-master cortex-package
    mv ./cortex-package/cortex-config/* $DPLOY_PATH/
    mv cortex $DPLOY_PATH/
    #mv cuda_miner $DPLOY_PATH/
    chmod +x ./cortex-package/service/cortex-monitor.sh
    mv ./cortex-package/service/cortex-monitor.sh /etc/init.d/cortex-monitor.sh
    update-rc.d cortex-monitor.sh defaults
    mv ./cortex-package/supervisor-config/cortexnode.conf /etc/supervisor/conf.d/cortexnode.conf

    supervisorctl reload
    sleep 5
    service cortex-monitor.sh start

    rm cortex-package.zip
    rm -r ./cortex-package

    echo deploy finish
}

helpdoc() {
    echo "Cortex full node deployment tool (version 0.1)"
    echo "Usage: sudo $0 [options] command"

    echo "Most used commands:"
    echo "  deploy - download and deploy cortex fullnode"
    echo "  install - deploy cortex fullnode from existing file"
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
