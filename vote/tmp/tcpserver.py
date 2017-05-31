from socket import *
import thread, sys
 
BUFF = 1024
HOST = '127.0.0.1'# must be input parameter @TODO
PORT = 12345      # must be input parameter @TODO

 
def handler(clientsock,addr):
    while 1:
        data = clientsock.recv(BUFF)
        if not data: 
           break
        sys.stdout.write(data)
        sys.stdout.flush()
    clientsock.close()
 
if __name__=='__main__':
    ADDR = (HOST, PORT)
    serversock = socket(AF_INET, SOCK_STREAM)
    serversock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    serversock.bind(ADDR)
    serversock.listen(10)
    while 1:
        print >> sys.stderr, 'waiting for connection...'
        clientsock, addr = serversock.accept()
        print >> sys.stderr, '...connected from:', addr
        thread.start_new_thread(handler, (clientsock, addr))
