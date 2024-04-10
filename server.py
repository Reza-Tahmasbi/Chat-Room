import threading
import socket

host = '127.0.0.1' # local
port = 15000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []

def broadcast(message):
    for client in clients:
        client.send(message)
    
# handling client, constantly trying to get message from client
# as soon as client casued any error, it means the client has left the chat
# and we are going to remove it from our server
    
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break
    
# accept clients all the time
# when the client connects, ask for nickname
# add the connected client to the chat
# start a thread to handle the connection for this particular client
def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        client.append(client)
        
        print(f"Nickname of client is {nickname}!")
        broadcast(f'{nickname} joined the chat!'.encode('ascii'))
        client.send("Connected to the server".encode('ascii'))
        
        thread = threading.Thread(target = handle, args = (client,))
        thread.start()
        
print("Server is listening...")
receive()