#!/usr/bin/python
import urllib2, json, subprocess, time

RefreshInterval = 60
CortexLogPath = '/tmp/cortex_fullnode_stderr.log'

def refresh():
    gpuinfo, macinfo, log = None, None, None

    try:
        process = subprocess.Popen(
            ''' nvidia-smi -q | awk -F: '$2 != " N/A" && $2 != "" {print $1, ",", $2}' ''',
            stdout=subprocess.PIPE, shell=True
        )
        gpuinfo, error = process.communicate()
        gpuinfo = [[item.strip() for item in x.strip().split(",")] for x in gpuinfo.split('\n') if x.find('N/A') == -1]
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
        process = subprocess.Popen(("tail -n 200 " + CortexLogPath).split(),
            stdout=subprocess.PIPE
        )
        log, error = process.communicate()
        log = [x for x in log.rstrip().split("\n")]
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
        process = subprocess.Popen("lscpu",
            stdout=subprocess.PIPE, shell=True
        )
        cpu_detail, error = process.communicate()
        process = subprocess.Popen("free -m",
            stdout=subprocess.PIPE, shell=True
        )
        memory_overview, error = process.communicate()
        info = {
            'ifconfig': ifconfig,
            'cpu_overview': cpu_overview,
            'cpu_detail': cpu_detail,
            'memory_overview': memory_overview,
        }
    except BaseException:
        pass

    data = { 'gpu': gpuinfo, 'mac': macinfo, 'log': log, 'info': info }

    try:
        req = urllib2.Request('http://monitor.cortexlabs.ai/nodelist/send')
        req.add_header('Content-Type', 'application/json')
        response = urllib2.urlopen(req, json.dumps(data))
    except BaseException:
        pass

if __name__ == '__main__':
    while True:
        refresh()
        time.sleep(RefreshInterval)

