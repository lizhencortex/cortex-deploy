#!/usr/bin/python
import urllib2, json, subprocess, time
import threading

version = 'Cortex Monitor 0.1.2'
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

def update_script():
    try:
        process = subprocess.Popen(
            'wget -q https://raw.githubusercontent.com/lizhencortex/cortex-deploy/master/cortex-config/cortex-monitor.py -O /opt/cortex/cortex-monitor.py.new',
            stdout=subprocess.PIPE, shell=True
        )
        process.communicate()
        process = subprocess.Popen(
            "cat /opt/cortex/cortex-monitor.py.new  | grep '/tmp/cortex_fullnode_stderr.log'",
            stdout=subprocess.PIPE, shell=True
        )
        content = process.communicate()
        if content == '':
            return
        process = subprocess.Popen(
            'diff /opt/cortex/cortex-monitor.py /opt/cortex/cortex-monitor.py.new',
            stdout=subprocess.PIPE, shell=True
        )
        diff_result = process.communicate()
        if diff_result != '':
            process = subprocess.Popen(
                'cat /opt/cortex/cortex-monitor.py | grep "version"',
                stdout=subprocess.PIPE, shell=True
            )
            version1 = process.communicate()
            process = subprocess.Popen(
                'cat /opt/cortex/cortex-monitor.py.new | grep "version"',
                stdout=subprocess.PIPE, shell=True
            )
            version2 = process.communicate()
            if ('No such file or directory' not in version1) or ('No such file or directory' not in version2):
                return
            if version1 == version2 or version2 == '':
                return

            process = subprocess.Popen(
                'mv /opt/cortex/cortex-monitor.py.new /opt/cortex/cortex-monitor.py',
                stdout=subprocess.PIPE, shell=True
            )
            process.communicate()
            process = subprocess.Popen(
                'service cortex-monitor restart',
                stdout=subprocess.PIPE, shell=True
            )
            process.communicate()
    except BaseException:
        pass

def upload_running_status():
    gpuinfo, macinfo, log = None, None, None

    try:
        process = subprocess.Popen('nvidia-smi -q', stdout=subprocess.PIPE, shell=True)
        gpuinfo, error = process.communicate()
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
        process = subprocess.Popen(
            "cat /sys/class/net/$(ip route show default | awk '/default/ {print $5}')/address",
            stdout=subprocess.PIPE, shell=True
        )
        macinfo, error = process.communicate()
        macinfo = macinfo.rstrip()
    except BaseException:
        pass

    try:
        process = subprocess.Popen(("tail -n 20 " + CortexLogPath).split(),
            stdout=subprocess.PIPE
        )
        log, error = process.communicate()
        log = [x for x in log.rstrip().split("\n")]
        process = subprocess.Popen(
            ''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":83}' 127.0.0.1:30089 ''',
            stdout=subprocess.PIPE, shell=True
        )
        blocknum = process.communicate()
    except BaseException:
        pass

    try:
        process = subprocess.Popen(
            ''' curl -X POST -H 'Content-Type: application/json' --data '{"jsonrpc":"2.0","method":"admin_nodeInfo","params":[],"id":83}' 127.0.0.1:30094 ''',
            stdout=subprocess.PIPE, shell=True
        )
        enodeInfo = process.communicate()
    except BaseException:
        pass

    try:
        process = subprocess.Popen("ifconfig | grep 'inet'",
            stdout=subprocess.PIPE, shell=True
        )
        ifconfig, error = process.communicate()
        process = subprocess.Popen("cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c",
            stdout=subprocess.PIPE, shell=True
        )
        cpu_overview, error = process.communicate()
        process = subprocess.Popen("free -m",
            stdout=subprocess.PIPE, shell=True
        )
        memory_overview, error = process.communicate()
        info = {
            'ifconfig': ifconfig,
            'cpu_overview': cpu_overview,
            'memory_overview': memory_overview,
            'blocknum': blocknum,
            'enodeInfo': enodeInfo,
        }
    except BaseException:
        pass

    data = { 'gpu': gpuinfo, 'mac': macinfo, 'log': log, 'info': info, 'version': version }

    try:
        req = urllib2.Request('http://monitor.cortexlabs.ai/api/send')
        req.add_header('Content-Type', 'application/json')
        req.add_header('Accept-Encoding', 'gzip')
        response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        pass

if __name__ == '__main__':
    set_interval(upload_running_status, RefreshInterval)
    set_interval(update_script, RefreshScriptInterval)
