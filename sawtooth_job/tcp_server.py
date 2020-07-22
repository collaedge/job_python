import sys
import struct
import select
import signal
import cPickle
from socket import *
HOST = '136.186.108.248'
def send(channel,*args):
  buffer = cPickle.dumps(args, protocol=2)
  value = htonl(len(buffer))
  size = struct.pack("L",value)
  channel.send(size)
  channel.send(buffer)
def receive(channel):
  size = struct.calcsize("L")
  size = channel.recv(size)
  try:
    size = ntohl(struct.unpack("L",size)[0])
  except struct.error as e:
    return ''
  buf = ''
  while len(buf) < size:
    buf += channel.recv(size-len(buf))
  return cPickle.loads(buf)[0]
 
class TcpServer(object):
  def __init__(self,PORT,backlog = 5):
    self.clients = 0
    self.clientmap = {}
    self.outputs = [] 
    self.server = socket(AF_INET, SOCK_STREAM)
    self.server.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    self.server.bind((HOST,PORT))
    self.server.listen(backlog)
    signal.signal(signal.SIGINT,self.signalhandler)
 
  def signalhandler(self,signum,frame):
    print("Shutting down server ...")
    for output in self.outputs:
      output.close()
    self.server.close()
 
  def get_client_name(self,client):
    info = self.clientmap[client]
    host,port,name = info[0][0],info[0][1],info[1]
    return ':'.join((('@'.join((name,host))),str(port)))
 
  def run(self):
    inputs = [self.server]
    print('Waiting for connect...')
    while True:
      try:
        readable,writeable,execption = select.select(inputs,self.outputs,[])
      except select.error as e:
        break
      for sock in readable:
        if sock == self.server:
          client,address = self.server.accept()
          print("server: connected from",address)
          self.clients += 1
          cname = receive(client)
          send(client,str(address[0]))
          inputs.append(client)
          self.clientmap[client] = (address,cname)
          msg = "(Connected : New Client(%d) from %s)\n"%(self.clients,self.get_client_name(client))
          for output in self.outputs:
            send(output,msg)
          self.outputs.append(client)
 
        #elif sock == sys.stdin:
          #break
        else:
          try:
            data = receive(sock)
            if data:
              msg = '[' + self.get_client_name(sock)+ '] >> ' + data
              for output in self.outputs:
                if output!=sock:
                  send(output,msg)
            else:
              self.clients-=1
              sock.close()
              inputs.remove(sock)
              self.outputs.remove(sock)
              msg = '(Now hung up: Client from %s)'%self.get_client_name(sock)
              for output in self.outputs:
                send(output,msg)
          except error as e:
            inputs.remove(sock)
            self.outputs.remove(sock)
    self.server.close()
if __name__ == "__main__":
    server = TcpServer(6004)
    server.run()