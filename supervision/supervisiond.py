import subprocess
import tempfile
import time
import re
import threading
import json



def pscan(ip):
    err = tempfile.TemporaryFile()
    try:
        result = str(subprocess.check_output(['fping', '-e', ip], stderr=err))
        delay = re.findall('\(([0-9\.]+) .*\)', result)
        return True, delay
    except subprocess.CalledProcessError as e:
        return False, 0



def get_hosts(filename):
    out = []
    with open(filename, 'r') as eqr:
        for host in eqr:
            data = host.split(',')
            out.append({
                    'name': data[1].strip('"'),
                    'ip': data[0],
                    'last_seen_up': None,
                    'scan_time': None,
                    'down': False,
                    'delay': None,
                    })
    return out




def scan(hosts):
        evt = threading.Event()
        while True:
            scan_time = time.time()
            success = []
            errors = []
            for host in hosts:
                result, delay = pscan(host['ip'])
                host['scan_time'] = int(scan_time)*1000
                if result:
                    success.append((host['name'], host['ip'], delay))
                    host['last_seen_up'] = int(scan_time)*1000
                    host['down'] = False
                    host['delay'] = delay[0]
                else:
                    errors.append((host['name'], host['ip']))
                    host['down'] = True
                    host['delay'] = 0
            with open('supervision/sup_out.json', 'w') as fp:
                json.dump(hosts, fp, indent=4)


            print(time.strftime('%H:%M:%S', time.localtime(scan_time)))
            e = evt.wait(timeout=300)


if __name__ == '__main__':
    hosts = get_hosts('supervision/equipements_reseau.csv')

    t = threading.Thread(target=scan, args=[hosts])
    print('**** Démarrage supervision ****')
    t.start()
