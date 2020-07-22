from socket import *
from time import ctime
import select
import sys
 
HOST = 'localhost'
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
tcpCliSock = socket(AF_INET, SOCK_STREAM)
tcpCliSock.connect(ADDR)
input = [tcpCliSock,sys.stdin]
 
while True:
	readyInput,readyOutput,readyException = select.select(input,[],[])
	for indata in readyInput:
		if indata==tcpCliSock:
			data = tcpCliSock.recv(BUFSIZ)
			print(data)
			if data=='88':
				break	
		else:
			data = raw_input('>')
			if data=='88':	
				tcpCliSock.send('%s' %(data))
				break
			tcpCliSock.send('[%s] %s' %(ctime(), data))
	if data=='88':	
		break
tcpCliSock.close()
