from sawtooth_job.tcp_server import send,receive
from socket import *
import sys
import select
import struct
import signal
 
class TcpClient(object):
  def __init__(self,name):
    self.name = name
    self.connected = False
    self.host = '136.186.108.248'
    self.port = 6004
    try:
      self.sock = socket(AF_INET,SOCK_STREAM)
      self.sock.connect((self.host,self.port))
      self.connected = True
    #   send(self.sock,self.name)
    #   data= receive(self.sock)
    #   addr = data
    except error as e:#socket.serro
      print('Failed to connect to server')
      sys.exit(1)
  def run(self):
    while True:
      try:
        readable,writeable,exception = select.select([0,self.sock],[],[])
        for sock in readable:
          if sock == 0:
            print('send data, format: task_name,base_rewards')
            data = sys.stdin.readline().strip()
            if data:
              send(self.sock,data)
          else:
            data=receive(self.sock)
            if not data:
              print('shutting down.')
              self.connected = False
              break
            else:
              sys.stdout.write(data+'\n')
              sys.stdout.flush()
      except KeyboardInterrupt:
        print('Client interrupted')
        self.sock.close()
        break
# if __name__ == "__main__":
#   name = raw_input("Please input login name > ")
#   client=TcpClient(name)
#   client.run()