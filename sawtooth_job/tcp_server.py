
from socket import *
from time import ctime
import select
import sys
 
HOST = ''
PORT = 21567
BUFSIZ = 1024
ADDR = (HOST, PORT)
 
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)
input = [tcpSerSock, sys.stdin] 
 
while True:
	print('waiting for connection...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('...connected from:',addr)
	input.append(tcpCliSock) 
	while True:
		readyInput,readyOutput,readyException = select.select(input,[],[])
		for indata in readyInput:
			if indata==tcpCliSock:
				data = tcpCliSock.recv(BUFSIZ)
				print(data)
				if data=='88':
					input.remove(tcpCliSock)
					break
			else:
				data = raw_input('>')
				if data=='88':
					tcpCliSock.send('%s' %(data))
					input.remove(tcpCliSock)
					break
				tcpCliSock.send('[%s] %s' %(ctime(), data))
		if data=='88':
			break
	tcpCliSock.close()
tcpSerSock.close()
