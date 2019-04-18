#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading
import re

tmpDir = '/tmp/cortex/'
updateUrl = 'https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/config.json'
RefreshScriptInterval = 3600
'https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/cortex-config/cortex.sh'

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

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
        sh('wget -q ' + updateUrl + ' -O ' + updateJsonPath)
        update = load_config(updateJsonPath)
        config = load_config('/opt/cortex/config.json')
        # cortexnode
        node_config = config.get('cortexnode', None)
        if node_config != None:
            if node_config['autoupdate'] == "enable" and ge(update['cortexnode']['version'], node_config['version']) :
                sh('wget -q' + node_config['url'] + ' -O /opt/')
                sh('mv /opt/cortex/cortex.sh.new /opt/cortex/cortex.sh')
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
            if monitor_config['autoupate'] == 'enable' and ge(update['monitor']['version'], monitor_config['version']) :
                sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/master/cortex-config/cortex-monitor.py -O /opt/cortex/cortex-monitor.py.new')
                sh('mv /opt/cortex/cortex-monitor.py.new /opt/cortex/cortex-monitor.py')
                sh('service cortex-monitor restart')
                config['monitor']['version'] = update['monitor']['version']

        save_config(config)
    except BaseException as e:
        print('error', e)
        pass

if __name__ == '__main__':
    set_interval(update, RefreshScriptInterval)
