import tqdm
import socket
import sys
import os
import threading
import time
import concurrent.futures




server = socket.socket()
HOST = "127.0.0.1"
port = 4000
SEPARATOR = "<SEPARATOR>"



#	The folder is received with the commandline argument supplied to the python commandline in index 1.

#	Concurrency is received with argument of index 2

#	$python3 client.py folder_sample 5

folder = sys.argv[1]
files = os.listdir(folder)
file_details = [(file,os.path.getsize(os.path.join(folder, file))) for file in files]

try:
	concurrency = sys.argv[2]
except IndexError as e:
	concurrency = 1

server.connect((HOST, port))
server.sendall(f"{len(files)}{SEPARATOR}{concurrency}".encode() + b'\n')
server.close()






#	Different files needs to be sent concurrently to the server across different connections.

#	Range(files, concurrency) will ensure that the files are sliced according to the concurrency value.

#	In each slice, a connection is mapped to each files in a slice. These connections will be handled concurrently by the server.


def Range(files,concurrency):
    d = concurrency
    b = 0
    w = files[b:concurrency]
    List = [w]
    while concurrency < len(files):
        b = concurrency
        concurrency += d
        w = files[b:concurrency]
        List.append(w)
    return(List)



#	The slicing occurs here with the Range() function

to_send = [segments for segments in Range(file_details, int(concurrency))]



#	Upload(conn, meta) handles the file transfer. 

#	conn --> connection

#	meta --> the key containing a tuple of filename and size


def upload(conn):
	filename = socket_with_file_dic[conn][0]
	filesize = socket_with_file_dic[conn][1]
	conn.sendall(f"{filename}".encode() + b'\n')
	progress = tqdm.tqdm(range(filesize), f"sending {filename}", unit = "B", unit_scale = True, unit_divisor=1024)
	with open(os.path.join(folder, filename), 'rb') as f:
		data = f.read()
		progress.update(len(data))
		conn.sendall(data)
		progress.close()


#	A loop is created to loop through the list of sliced files to be sent. 

#	A connection is mapped to a file each and sent to the server.

# 	As the connections are being created, the server handles the connections concurrently. 

#	The files are sents in batches of the concurrency value



	
start = time.perf_counter()

# a loop is initiated to get the slice containing the files to be sent at once

for file in to_send:
	
	connections = [socket.socket() for sock in range(int(concurrency))]

	for conn in connections:
		conn.connect((HOST, port))

	socket_with_file = zip(connections, file)
	socket_with_file_dic = dict(socket_with_file)
	with concurrent.futures.ThreadPoolExecutor() as executor:
		executor.map(upload, (socket_with_file_dic))
finish = time.perf_counter()


#	concurrent.futures is used to send the files in a slice concurrently. 

#	So if 5 files are in a slice, the five files won't be sent one by one but concurrently. 

#	The server has also been setup to handle the file downloads concurrenly

#	The total time taken to send all the files across all connections is computed

throughput = round(len(files)/round(finish-start, 2), 2)

print(f'''

	All files were sent with concurrency {concurrency} with throughput of {throughput}


	*******************CONCURRENCY******************************THROUGHPUT***********************
	*********************************************************************************************
	*******************{concurrency}						{throughput} ************************

	''')

