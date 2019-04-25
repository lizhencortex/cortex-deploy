#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading

version = 'Cortex Monitor 0.1.3'
RefreshInterval = 60

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
    if ret != None :
        return ret
    else:
        raise Exception(command + 'failed,' + err)

def load_config(path):
    with open(path, 'r') as raw_config:
        config = json.load(raw_config)
    return config


def upload_running_status():
    gpuinfo, dmiinfo, info, config = None, None, None, None

    try:
        gpuinfo = sh('nvidia-smi -q')
        gpuinfo = [x for x in gpuinfo.decode("utf-8") .split('\n') if 'N/A' not in x][3:]

        root = {}
        stack = [root]
        last_indent = 0
        for x in gpuinfo:
            indent = len(x) - len(x.lstrip())
            left = x.split(':')[0].strip()
            right = x.split(':')[1].strip() if ':' in x else None
            current = left + (' ' + right if right != None else '')
            if indent > last_indent:
                stack[-1][last] = {}
                stack.append(stack[-1][last])
            if left != 'GPU 00000000' and left != 'Process ID' and left != '':
                stack[-1][left] = right
            if indent < last_indent:
                stack = stack[:-int((last_indent - indent) / 4)]
            last = current
            last_indent = indent
        gpuinfo = root
    except BaseException:
        pass

    try:
        blocknum = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83}' 127.0.0.1:30089 ''')
        enodeInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_nodeInfo","params":[],"id":83}' 127.0.0.1:30089 ''')
        peersInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_peers","params":[],"id":83}' 127.0.0.1:30089 ''')
    except BaseException:
        pass

    try:
        dmiinfo = sh("dmidecode -t 4 | grep ID | sed 's/.*ID://;s/ //g'").strip('\n')
        ifconfig = sh("ifconfig | grep 'inet'")
        cpu_overview = sh("cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c")
        memory_overview = sh("free -m")
        info = {
            'ifconfig': ifconfig,
            'cpu_overview': cpu_overview,
            'memory_overview': memory_overview,
            'blocknum': blocknum,
            'enodeInfo': enodeInfo,
            'peersInfo': peersInfo,
        }
        config = load_config('/opt/cortex/config.json')
    except BaseException:
        pass

    data = { 'gpu': gpuinfo, 'dmi': dmiinfo, 'info': info, 'config': config, 'version': version }

    try:
        req = urllib2.Request('http://monitor.cortexlabs.ai/testapi/send')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        pass

if __name__ == '__main__':
    set_interval(upload_running_status, RefreshInterval)

