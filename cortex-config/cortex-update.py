#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading
import re


updateUrl = 'https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/config.json'
tmpDir = '/tmp/cortex/'
configDir = '/opt/cortex/'

RefreshScriptInterval = 3600

#'https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/cortex-config/cortex.sh'

# rx
CUDA = re.compile(r'CUDA_VERSION')
coinbase = re.compile(r'(MINER_COINBASE)=(\'0x[0-9|a-f]{40}\')')
port = re.compile(r'(--port)\s(\d+)')
rpcapi = re.compile(r'(--rpcapi)\s([\w+,]+\w+)')


def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def update_script(node_config):
    nodePath = configDir + "cortex.sh"
    cortexnode = sh('cat ' + nodePath)
    d = dict()
    
    d[port] = "--port " + node_config["port"]
    d[rpcapi] = "--rpcapi " + node_config["rpcapi"]
    d[coinbase] = "MINER_COINBASE=" + node_config["MINER_COINBASE"]
    d[CUDA] = "cuda-" + node_config["cuda_version"]
    
    for key, value in d.items():
        cortexnode = re.sub(key, value, cortexnode)
    
    with open(nodePath, 'w+') as f:
        f.write(cortexnode)
        f.close()

def ge(v1, v2):
    v1 = re.split('\.', v1)
    v2 = re.split('\.', v2)

    v1 = [int(v1[i]) for i in range(len(v1))]
    v2 = [int(v2[i]) for i in range(len(v2))]

    if(v1 >= v2):
        return True
    else:
        return False

def sh(command):
    p = Popen(command, stderr=PIPE, stdout=PIPE, shell=True)
    ret, err = p.communicate()
    if ret != None :
        return ret
    else:
        raise Exception(command + 'failed,' + err)

def load_config(path):
    with open(path, 'r') as raw_config:
        config = json.load(raw_config)
    return config

def save_config(config):
    with open('/opt/cortex/config.json', 'w') as f:
        f.write(json.dumps(config))
        f.close()

def update():
    try:
        sh('rm -r ' + tmpDir)
        sh('mkdir -p ' + tmpDir)
        updateJsonPath = tmpDir + 'update.json'
        configJsonPath = configDir + 'config.json'
        sh('wget -q ' + updateUrl + ' -O ' + updateJsonPath)
        update = load_config(updateJsonPath)
        config = load_config(configJsonPath)

        # cortexnode
        node_config = config.get('cortexnode', None)
        if node_config != None:
            if node_config['autoupdate'] == "enable" and ge(update['cortexnode']['version'], node_config['version']) :
                sh('wget -q ' + node_config['url'] + ' -O ' + tmpDir)
                update_script(node_config)
                sh('supervisorctl restart cortexnode')
                config['cortexnode']['version'] = update['cortexnode']['version']
        # minerpool
        minerpool_config = config.get('minerpool', None)
        if minerpool_config != None:
            pass

        # miner
        miner_config = config.get('miner', None)
        if miner_config != None:
            pass

        # monitor
        monitor_config = config.get('monitor', None)
        if monitor_config != None:
            if monitor_config['autoupdate'] == 'enable' and ge(update['monitor']['version'], monitor_config['version']) :
                sh('wget -q ' + monitor_config['url'] + '-O' + tmpDir)
                sh('mv ' + tmpDir + 'cortex-monitor.py' + configDir + 'cortex-monitor.py')
                sh('service cortex-monitor restart')
                config['monitor']['version'] = update['monitor']['version']

    except BaseException as e:
        print('error', e)
        config['error_log'] = e
        pass
    
    save_config(config)

if __name__ == '__main__':
    set_interval(update, RefreshScriptInterval)
