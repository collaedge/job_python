import socket
import select
import sys

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
        while True:
            try:
                readable,writeable,exception = select.select([0,self.sock],[],[])
                for sock in readable:
                    if sock == 0:
                        # input format <msg_type,task_name,base_rewards>
                        tmp = sys.stdin.readline().strip()
                        if tmp:
                            data = self.name + ',' + tmp
                            self.sock.send(data.encode('utf8'))
                    else:
                        data = sock.recv(1024).decode('utf-8')
                        if data:
                            sys.stdout.write(data+'\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print('Client interrupted')
                self.sock.close()
                break
# if __name__ == "__main__":
#     name = input("Please input login name > ")
#     client=client(name)
#     client.run()