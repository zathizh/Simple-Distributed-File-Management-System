import socket
import optparse
import tempfile
from time import gmtime, strftime
from threading import Thread

sdfm=[]

def get_table(client):
	if not len(sdfm) == 0:
		rc = ""
		for record in sdfm:
			fname = record[0] if not record[0] =='' else "None"
			loc =   record[1] if not record[1] =='' else "None"
			port =  record[2] if not record[2] =='' else "None"
			u_t =   record[3] if not record[3] =='' else "None"
			d_t =   record[4] if not record[4] =='' else "None"
			t_d =   record[5] if not record[5] == 0 else 0
			rc = rc + fname + "\nLocation : " + loc + ", " + str(port) + "\nUpload Time : " + u_t + \
				"\nLast Download Time : " + d_t + "\nTotal Downloads : " + str(t_d) + "\n"
		client.send(rc)
	else:
		client.send("No Entry")

def _quit(client, addr):
	length = len(sdfm)
	i = 0
	if length:
                for j in range(length):
                        if sdfm[i][1] == addr:
                                del sdfm[i]
                                length = length - 1
                                continue
                        i = i + 1
                client.send("Entries Cleared")
        else :
                client.send("No Entries Found")
	client.close()
	print(addr + " " + " Disconnected")

def delete(cmnd, client, addr):
	l = len(sdfm)
	for i in range(l):
		if sdfm[i][1] == addr and sdfm[i][0] == cmnd[1]:
			del sdfm[i]
			client.send("Record Deleted")
			break
##		if sdfm[i][1] == addr and not sdfm[i][0]== cmnd[1]:
##			client.send("You are not authorized to Delete " + cmnd[1])
##			break
	if len(sdfm) == l:
		client.send("No record found")

def upload(cmnd, client, addr):
	t = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
	entry = [str(cmnd[1]), addr, int(cmnd[2]), str(t), '', 0]
	sdfm.append(entry)
	notify = "added : " + str(t) + " " + cmnd[1] + " " + addr
	client.send(notify)

def download(cmnd, client, addr):
        fname = cmnd[1]
        d_port = int(cmnd[2])
        checker = 0
        for record in sdfm:
                if record[0] == fname:
                        checker = 1
                        d_sock = socket.socket()

                        fp = tempfile.TemporaryFile()
                        d_sock.connect((record[1], int(record[2])))
                        d_sock.send("upload " + fname)
                        while True:
                                data = d_sock.recv(1024)
                                if not data:
                                        break
                                fp.write(data)
                        fp.seek(0)

                        fp.seek(0)
                        d_sock.close()
                        
                        n_sock = socket.socket()
                        n_sock.connect((addr, d_port))
                        n_sock.send("download " + fname)
                        n_sock.recv(1024)
                        while True:
                                data = fp.read(1024)
                                if not data:
                                        break
                                n_sock.send(data)
                        fp.close()
                        n_sock.close()
                        t = strftime("%a, %d %b %Y %H:%M:%S", gmtime())
                        sdfm[sdfm.index(record)][4] = t
                        sdfm[sdfm.index(record)][5] = int(record[5]) + 1
                        print("File Download Completed")
                        client.send("Download Completed " + str(t))
                        break
        if not checker :
                d_sock = socket.socket()
                d_sock.connect((addr, d_port))
                d_sock.send("close")
                d_sock.close()
                client.send("File Not Found")


def conn(client, adr):
	client.settimeout(120)
	addr = str(adr[0]) 
	print(addr),
	print(" Connected")
	client.send("Simple Distributed File Management Server")
	while True:
		try:
			cmnd = client.recv(1024)
			if cmnd == b'':
				break
			cmnd = cmnd.strip().split()
			operation = cmnd[0].lower()
			if operation == "upload" and len(cmnd) == 3:
				upload(cmnd, client, addr)
			elif operation == "upload" and not len(cmnd) == 3:
				client.send("usage : upload <filename>")

			elif operation == "delete" and len(cmnd) == 2:
				delete(cmnd, client, addr)
			elif operation == "delete" and not len(cmnd) == 2:
				client.send("usage : delete <filename>")

			elif operation == "download" and len(cmnd) == 3:
                                t = Thread(target = download, args=(cmnd, client, addr,))
                                t.daemon = True
                                t.start()
##                                download(cmnd, client, addr)
			elif operation == "download" and not len(cmnd) == 3:
				client.send("usage : download <filename>")

			elif operation == "get" and cmnd[1] == "table" and len (cmnd) == 2:
				get_table(client)

			elif operation == "quit":
				_quit(client, addr)
				break
			else :
				client.send("invalid command\nusage : upload <filename>| delete <filename>| download <filename> | get table | quit")
		except socket.error as ex:
			print("[-] Timeout")
			break
		except Exception as ex:
                        print(ex)
			client.close()
			break
	client.close()

def main():
        parser = optparse.OptionParser("usage %prog -c [control port]")
        parser.add_option("-c", dest="cport", type="int", help="specify control port")
        (options, args) = parser.parse_args()
        c_port = options.cport
        if c_port:
                c_sock = socket.socket()
                c_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	
                host = '127.0.0.1'
                c_sock.bind((host, c_port))
                c_sock.listen(5)
	
                print("[+] Starting Simple Distributed Management Server")

                try:	
                        while True:
                                try:
                                        client, addr = c_sock.accept()
                                        t = Thread(target=conn, args=(client,addr))
                                        t.daemon = True
                                        t.start()
                                except Exception as ex:
                                        print(ex)
                except KeyboardInterrupt:
                        print("")
                        print("[-] Exiting Simple Distributed Management Server")
        else:
                print("usage %prog -c [control port]")

if __name__ == '__main__':
	main()
