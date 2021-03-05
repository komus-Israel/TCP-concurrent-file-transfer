import socket
import sys
import threading
import time
import tqdm
import os


server = socket.socket()
HOST = "127.0.0.1"
port = 4000
SEPARATOR = "<SEPARATOR>"




print("starting up on %s port %s" %(HOST, port))
server.bind((HOST, port))

server.listen()
print("Listening for connection")

client, address = server.accept()
no_files, concurrency  = client.recv(1024).decode().split(SEPARATOR)
client.close()



#	The download path for the server needs to created if it doesnt exist.

#	If it exist, then it won't be created


download_path = os.path.join(os.getcwd(), 'server_files')
os.makedirs(download_path, exist_ok = True)

def handle_clients(client):

	
	with client, client.makefile('rb') as clientfile:		
		try:
				
			filename = clientfile.readline().strip().decode()
			data = clientfile.read()
			
			
		except UnicodeDecodeError as e:

			data = clientfile.read()
			filename = clientfile.readline().strip().decode()
		finally:
			length = len(data)
		try:

			#if len(data) < 2:
			#	pass
			#else:
				progress = tqdm.tqdm(range(length), f"Receiving {filename}", unit = "B", unit_scale = True, unit_divisor=1024)
				with open(os.path.join(download_path, filename) , 'wb') as file:			
					file.write(data)
					progress.update(len(data))
				print()
		except FileNotFoundError as e:
			pass
		finally:
			client.close()



#	This thread handles all connected clients concurrently. It ensures that 

#	the files are received from connected clients concurrently because the clients are  connected concurrently.

#	However, if concurrency == 1, the files are sent one by one. concurrency greater than two are handled concurrently





for i in range(int(no_files)):



	if int(concurrency) == 1:
		client, address = server.accept()
		print(f"{address} is connected")

		handle_clients(client)
	else:
		client, address = server.accept()
		print(f"{address} is connected")

		try:
			thread = threading.Thread(target = handle_clients, args = [client])
			thread.start()
		except AssertionError as e:
			pass
	



	
	
	
	
	

	

	


	



	
