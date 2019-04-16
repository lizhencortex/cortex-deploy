#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading

version = 'CortexAutoUpdate 1.0.0'
RefreshScriptInterval = 3600

def set_interval(func, sec):
    def func_wrapper():
        set_interval(func, sec)
        func()
    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t

def sh(command):
    p = Popen(command, stderr=PIPE, stdout=PIPE, shell=True)
    ret, err = p.communicate()
    if err != None:
        raise Exception(err)
    else:
        return ret

def load_config():
    with open('/opt/cortex/config.json', 'r') as raw_config:
        config = json.load(raw_config)
    return config

def save_config(config):
    with open('opt/cortex/config.json', 'w') as f:
        f.write(json.dumps(config))
        f.close()

def update():
    try:
        sh('wget -q ')

        config = load_config()
        node_config = config.get('node', None)
        if node_config != None:
            pass

        minerpool_config = config.get('minerpool', None)
        if minerpool_config != None:
            pass

        miner_config = config.get('miner', None)
        if miner_config != None:
            pass
        save_config(config)
    except BaseException:
        pass

if __name__ == '__main__':
    set_interval(update, RefreshScriptInterval)
