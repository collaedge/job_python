import socket
import select
import sys
import time
import psutil
import os

from sawtooth_job.job_client import JobClient

class TcpClient:
    def __init__(self,name):
        self.name = name
        self.host = '136.186.108.248'
        self.port = 6009
        try:
            self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            self.sock.connect((self.host,self.port))
            # self.sock.send(self.name.encode('utf8'))
        except:
            print('Failed to connect to chat server')
            sys.exit(1)
    def run(self):
        req_user = ''
        workers = []
        req_rewards = 0
        while True:
            try:
                readable,writeable,exception = select.select([0,self.sock],[],[])
                for sock in readable:
                    start_time = 0
                    end_time = 0
                    if sock == 0:
                        # input format <msg_type,task_name,base_rewards>
                        tmp = sys.stdin.readline().strip()
                        if tmp:
                            req_user = self.name
                            req_rewards = float(tmp.split(',')[2])
                            data = self.name + ',' + tmp
                            self.sock.send(data.encode('utf-8'))
                    else:
                        data = sock.recv(1024).decode('utf-8')
                        if data:
                            data_list = data.split(',')
                            if data_list[1] == 'req':
                                # whether accept req
                                req_user = data_list[0]
                                sys.stdout.write('received req from '+req_user+' data: '+data+'\n')
                                sys.stdout.flush()
                                cpu_usage = psutil.cpu_percent()
                                sys.stdout.write('cpu_usage '+str(cpu_usage)+'\n')
                                sys.stdout.flush()
                                if cpu_usage < 50.0 :
                                    self.sock.send((self.name+',res,yes').encode('utf-8'))
                            elif data_list[1] == 'res' and req_user == self.name:
                                sys.stdout.write('req_user: '+req_user+' data: '+data+'\n')
                                sys.stdout.flush()
                                job_client = JobClient(base_url='http://127.0.0.1:8008', keyfile=None)
                                # choose workers
                                workers.append(data.split(',')[0])
                                if len(workers) == 3 or len(workers) == 6:
                                    s = job_client.chooseWorker2(workers)
                                    sys.stdout.write(s+'\n')
                                    sys.stdout.flush()
                                    str_out = 'do,' + s
                                    self.sock.send(str_out.encode('utf-8'))
                                    workers.clear()
                            elif data_list[1] == self.name and data_list[0] == 'do':
                                keyfile = get_keyfile(self.name)
                                job_client = JobClient(base_url='http://127.0.0.1:8008', keyfile=keyfile)
                                start_time = time.time()
                                time.sleep(5)
                                end_time = time.time()
                                job_client.create(self.name, req_user, start_time, end_time, 5500, req_rewards)

            except KeyboardInterrupt:
                print('Client interrupted')
                self.sock.close()
                break

    def get_keyfile(self, username):
        home = os.path.expanduser("~")
        key_dir = os.path.join(home, ".sawtooth", "keys")
        return '{}/{}.priv'.format(key_dir, username)
# if __name__ == "__main__":
#     name = input("Please input login name > ")
#     client=client(name)
#     client.run()