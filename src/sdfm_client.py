import socket
import sys
import os
import subprocess
from threading import Thread

mode = 0
threads = []

def u_listner(client, fname):
    fp = open(fname, 'rb')
    if fp:
        while True:
            data = fp.read(1024)
            if not data:
                break
            client.send(data)
        fp.close()
    client.close()
##    print("File Upload Completed")
        
def d_listner(client, fname):
    with open (fname, 'wb') as fp:
        while True:
            data = client.recv(1024)
            if not data:
                break
            fp.write(data)
    client.close()
##    print("File Download Completed")

def listner(d_sock, d_port):
    try:
        while True:
            client, addr = d_sock.accept()
            info = client.recv(1024).strip().split()
            operation = info[0].lower()
            if operation == "upload" and len(info) == 2:
                t = Thread(target=u_listner, args=(client, info[1]))
                t.daemon = True
                t.start()
##                t.join()
            elif operation == "download" and len(info) == 2:
                client.send("start")
                t = Thread(target=d_listner, args=(client, info[1]))
                t.daemon = True
                t.start()
##                t.join()
##                if not len(threads):
##                    t = Thread(target=d_listner, args=(client, info[1]))
##                    t.daemon = True
##                    t.start()
##                elif len(threads):
##                    thread = threads[0]
##                    if not thread.is_alive():
##                        thread.start()
            elif operation == "close":
                client.close()
            if not mode:
                threads.pop()
                break
    except Exception as ex:
        print(ex)
        
def conn(c_sock, d_sock, d_port):
    header = c_sock.recv(1024).strip()
    print(header)
    while True:
        cmnd = raw_input().strip()
        chunk = cmnd.split()
        operation = chunk[0].lower()
        if   operation == "upload" and len(chunk) == 2:
            fname = chunk[1]
            if fname in os.listdir(os.getcwd()):
                c_sock.send(cmnd + " " + str(d_port))
                mode = 1
                if not len(threads):
                    t = Thread(target = listner, args=(d_sock, d_port,))
                    t.daemon = True
                    threads.append(t)
                    t.start()
                elif len(threads):
                    thread = threads[0]
                    if not thread.is_alive():
                        thread.start()
            else :
                print("File not Found")
                continue
        elif operation == "download" and len(chunk) == 2:
            c_sock.send(cmnd + " " + str(d_port))
            if not len(threads):
                t = Thread(target = listner, args=(d_sock, d_port,))
                t.daemon = True
                threads.append(t)
                t.start()
            elif len(threads):
                thread = threads[0]
                if not thread.is_alive():
                    thread.start()
        elif operation == "delete" and len(chunk) == 2:
            c_sock.send(cmnd)
        elif operation == "get" and len(chunk) == 2 and chunk[1].lower() == "table":
            c_sock.send(cmnd)
            print("")
        elif operation == "quit":
            c_sock.send(cmnd)
            break
        elif operation == "ls":
            subprocess.call(["ls"])
            continue
        else :
            print("Invalid Input")
            print("usage upload <filename> | download <filename> | delete <filename> | get table | quit")
            continue
        data = c_sock.recv(1024)
        print(data)
        
        
def main():
    try:
        c_sock = socket.socket()
	c_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        d_sock = socket.socket()
	d_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = "127.0.0.1"
        c_port = 52001
        d_port = int(sys.argv[1])
        c_sock.connect((host, c_port))
        d_sock.bind((host, d_port))
        d_sock.listen(5)
        conn(c_sock, d_sock, d_port)
    except KeyboardInterrupt:
        print("[-] SFDM Client Quiting")
    except Exception as ex:
        print(ex)

if __name__ == '__main__':
    main()
