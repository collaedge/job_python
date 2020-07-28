import subprocess

def run():
    count = 0
    while count < 20:
        p = subprocess.Popen(['~/development/ycsb-0.17.0/bin/ycsb.sh run basic -P ~/development/ycsb-0.17.0/workloads/workloada -p operationcount=200000'], shell = True)
        p.wait()
        count = count + 1

run()