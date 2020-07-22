
# from socket import *
# from time import ctime
# import select
# import sys
 
# HOST = ''
# PORT = 21567
# BUFSIZ = 1024
# ADDR = (HOST, PORT)
 
# tcpSerSock = socket(AF_INET, SOCK_STREAM)
# tcpSerSock.bind(ADDR)
# tcpSerSock.listen(7)
# input = [tcpSerSock, sys.stdin] #input是一个列表，初始有欢迎套接字以及标准输入
 
# while True:
# 	print('waiting for connection...')
# 	tcpCliSock, addr = tcpSerSock.accept()
# 	print('...connected from:',addr)
# 	input.append(tcpCliSock) #将服务套接字加入到input列表中
# 	while True:
# 		readyInput,readyOutput,readyException = select.select(input,[],[]) #从input中选择，轮流处理client的请求连接（tcpSerSock），client发送来的消息(tcpCliSock)，及服务器端的发送消息(stdin)
# 		for indata in readyInput:
#             #处理client发送来的消息
# 			if indata==tcpCliSock:
# 				data = tcpCliSock.recv(BUFSIZ)
# 				print(data)
# 				if data=='88':
# 					input.remove(tcpCliSock)
# 					break
# 			else: #处理服务器端的发送消息
# 				data = raw_input('>')
# 				if data=='88':
# 					tcpCliSock.send('%s' %(data))
# 					input.remove(tcpCliSock)
# 					break
# 				tcpCliSock.send('[%s] %s' %(ctime(), data))
# 		if data=='88':
# 			break
# 	tcpCliSock.close()


from server import send,receive
from socket import *
import sys
import select
import cPickle
import struct
import signal
 
class ChatClient(object):
    def __init__(self,name):
        self.name = name
        self.connected = False
        self.host = 'localhost'
        self.port = 6004
        try:
            self.sock = socket(AF_INET,SOCK_STREAM)
            self.sock.connect((self.host,self.port))
            self.connected = True
            send(self.sock,self.name)
            data= receive(self.sock)
            addr = data
        except error,e:#socket.serro
            print 'Failed to connect to chat server'
            sys.exit(1)
    def run(self):
        while True:
            try:
                readable,writeable,exception = select.select([0,self.sock],[],[])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip()
                        if data:
                            send(self.sock,data)
                    else:
                        data=receive(self.sock)
                        if not data:
                            print 'Client shutting down.'
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data+'\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print 'Client interrupted'
                self.sock.close()
                break
if __name__ == "__main__":
    name = raw_input("Please input login name > ")
    client=ChatClient(name)