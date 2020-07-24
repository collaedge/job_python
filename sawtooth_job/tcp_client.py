import socket
import select
import sys
import time

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
                                self.sock.send((self.name+',res,yes').encode('utf-8'))
                            elif data_list[1] == 'res' and req_user == self.name:
                                sys.stdout.write('req_user: '+req_user+' data: '+data+'\n')
                                sys.stdout.flush()
                                job_client = JobClient(base_url='http://127.0.0.1:8008', keyfile=None)
                                # choose workers
                                workers.append(data.split(',')[0])
                                if len(workers) == 2 or len(workers) == 3 or len(workers) == 6:
                                    s = job_client.chooseWorker2(workers)
                                    sys.stdout.write(s+'\n')
                                    sys.stdout.flush()
                                    str_out = 'do,' + s
                                    self.sock.send(str_out.encode('utf-8'))
                            elif data_list[1] == self.name and data_list[0] == 'do':
                                job_client = JobClient(base_url='http://127.0.0.1:8008', keyfile=None)
                                start_time = time.time()
                                time.sleep(5)
                                end_time = time.time()
                                job_client.create(self.name, req_user, start_time, end_time, 5500, 20)

            except KeyboardInterrupt:
                print('Client interrupted')
                self.sock.close()
                break
# if __name__ == "__main__":
#     name = input("Please input login name > ")
#     client=client(name)
#     client.run()