#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading
import re

version = 'Cortex Monitor 0.1.3'
RefreshInterval = 60
RefreshScriptInterval = 3600
CortexLogPath = '/tmp/cortex_fullnode_stderr.log'

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
    if err != None:
        raise Exception(command + 'failed, ' + err)
    else:
        return ret

def update_script():
    try:
        sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/master/cortex-config/cortex-monitor.py -O /opt/cortex/cortex-monitor.py.new')
        diff = sh('diff /opt/cortex/cortex-monitor.py /opt/cortex/cortex-monitor.py.new')
        if diff != '':
            version1 = sh('cat /opt/cortex/cortex-monitor.py | grep "version"')
            version2 = sh('cat /opt/cortex/cortex-monitor.py.new | grep "version"')
            if ('No such file or directory' not in version1) or ('No such file or directory' not in version2):
                return
            if version1 == version2 or version2 == '':
                return

            sh('mv /opt/cortex/cortex-monitor.py.new /opt/cortex/cortex-monitor.py')
            sh('service cortex-monitor restart')
    except BaseException:
        pass

def update_Allscripts():
    try :
        sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/cortex-config/version.json -O /opt/cortex/version.json.new')
        version_diff = sh('diff /opt/cortex/version.json /opt/cortex/version.json.new')
        if version_diff != '':
            with open("/opt/cortex/version.json", 'r') as load_f1:
                version1 = json.load(load_f1)
            
            with open("/opt/cortex/version.json.new", 'r') as load_f2:
                version2 = json.load(load_f2)

            # update cortex 
            if version1['cortex']['exist'] and ge(version2['cortex']['version'], version1['cortex']['version']) :
                sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/xy/cortex-config/cortex.sh -O /opt/cortex/cortex.sh.new')
                sh('mv /opt/cortex/cortex.sh.new /opt/cortex/cortex.sh')
                sh('supervisorctl restart cortexnode')
                version1['cortex']['version'] = version2['cortex']['version']
            # update miner

            # update minerpool

            # update monitor
            if version1['monitor']['exist'] and ge(version2['monitor']['version'], vresion1['monitor']['version']) :
                sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/master/cortex-config/cortex-monitor.py -O /opt/cortex/cortex-monitor.py.new')
                sh('mv /opt/cortex/cortex-monitor.py.new /opt/cortex/cortex-monitor.py')
                sh('service cortex-monitor restart')
    except BaseException:
        pass


def upload_running_status():
    gpuinfo, macinfo, log = None, None, None

    try:
        gpuinfo, error = sh('nvidia-smi -q', stdout=PIPE, shell=True)
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
#        sh(("tail -n 20 " + CortexLogPath).split(),
#            stdout=PIPE
#        )
#        log, error =         log = []
        blocknum = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83}' 127.0.0.1:30089 ''')
        enodeInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_nodeInfo","params":[],"id":83}' 127.0.0.1:30089 ''')
        peersInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_peers","params":[],"id":83}' 127.0.0.1:30089 ''')
    except BaseException:
        pass

    try:
        macinfo = sh("cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address")
        macinfo = macinfo.rstrip()
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
    except BaseException:
        pass

    data = { 'gpu': gpuinfo, 'mac': macinfo, 'log': log, 'info': info, 'version': version }

    try:
        req = urllib2.Request('http://monitor.cortexlabs.ai/testapi/send')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        pass

if __name__ == '__main__':
   set_interval(upload_running_status, RefreshInterval)
   set_interval(update_ALLscripts, RefreshInterval)