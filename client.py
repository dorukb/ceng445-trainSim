from socket import *
from threading import Thread

run = True
def client():
    global run
    # the connection is kept alive until client closes it.
    c = socket(AF_INET, SOCK_STREAM)
    c.connect(('127.0.0.1', 34377))

    t = Thread(target = receiver, args=(c,))
    t.start()

    command = input()
    while command != "BYE":
        if(not run): break
        c.send(command.encode())
        command = input()

    run = False
    t.join()
    c.close()

def receiver(sock):
    global run
    while run:
        reply = sock.recv(16384)    
        if(len(reply.decode()) < 1):
            run = False
            break
        print(reply.rstrip().decode())
        
    return

if __name__ == '__main__':
	client()