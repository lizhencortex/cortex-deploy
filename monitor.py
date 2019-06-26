#!/usr/bin/python
import urllib2, json, time
from subprocess import PIPE, Popen
import threading

version = 'Cortex Monitor 0.1.3'
port = 30089
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

def sh(command):
    p = Popen(command, stderr=PIPE, stdout=PIPE, shell=True)
    ret, err = p.communicate()
    if err != None:
        raise Exception(err)
    else:
        return ret

def update_script():
    try:
        sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/dev/version.txt -O /tmp/version.txt.new')
        version_diff = sh('diff /opt/cortex/version.txt /tmp/version.txt.new')
        if version_diff != '':
            version1 = sh('cat /opt/cortex/version.txt')
            version2 = sh('cat /tmp/version.txt.new')
            if version2 >= version1 or version2 == '':
                return
            sh('wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/dev/cortex-monitor.py -O /tmp/cortex-monitor.py.new')
            sh('mv /tmp/cortex-monitor.py.new /opt/cortex/cortex-monitor.py')
            sh('mv /tmp/version.txt.new /opt/cortex/version.txt')
            sh('service cortex-monitor restart')
    except BaseException:
        pass

def upload_running_status():
    gpuinfo, macinfo, log = None, None, None

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
        blocknum = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"ctxc_blockNumber","params":[],"id":83}' 127.0.0.1:''' + str(port))
        enodeInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_nodeInfo","params":[],"id":83}' 127.0.0.1:''' + str(port))
        peersInfo = sh(''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_peers","params":[],"id":83}' 127.0.0.1:''' + str(port))
    except BaseException:
        pass

    try:
        macinfo = sh("cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address")
        macinfo = macinfo.rstrip()
        ifconfig = sh("ifconfig | grep 'inet'")
        kernel_version = sh("uname -a")
        os_version = sh("head -n 1 /etc/issue")
        hostname = sh("hostname")
        cpu_overview = sh("cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c")
        memory_overview = sh("free -m")
        info = {
            'ifconfig': ifconfig,
            'cpu_overview': cpu_overview,
            'memory_overview': memory_overview,
            'blocknum': blocknum,
            'enodeInfo': enodeInfo,
            'peersInfo': peersInfo,
            'kernel_version': kernel_version,
            'os_version': os_version,
            'hostname': hostname,
        }
    except BaseException:
        pass

    data = { 'gpu': gpuinfo, 'mac': macinfo, 'log': log, 'info': info, 'version': version }

    try:
        req = urllib2.Request('http://monitor.cortexlabs.ai/apiv3/send')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        pass

if __name__ == '__main__':
   set_interval(upload_running_status, RefreshInterval)
   set_interval(update_script, RefreshScriptInterval)
