import threading
import sqlite3
import socket

host = '127.0.0.1' # local
port = 15000

conn = sqlite3.connect('your_database.db')
c = conn.cursor()
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
def login(user_input, client):
    username = input(user_input.split()[1])
    password = input(user_input.split()[2])
    if ' ' in username():
        return "username must not include white space", False
    if ' ' in password:
        return "password must not include white space", False
    results = c.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
    results = c.fetchall()
    if results:
        return "You have logged in successfuly!", True
    else:
        client.close()

def register(user_input):
    username = input(user_input.split()[1])
    password = input(user_input.split()[2])
    if ' ' in username():
        return "username must not include white space", False
    if ' ' in password:
        return "password must not include white space", False
    results = c.execute("SELECT * FROM user WHERE username=?", (username,))
    results = c.fetchall()
    if results:
        return "username already exists!", False
    else:
        c.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        return "You are successfully Registered!", True

def generate_key(password):
    C
    
def receive():
    while True:
        first_time = True
        client, address = server.accept()
        print(f"Connected with {str(address)}")


        if first_time:
            # Choose what to do?
            server_mess = """
                    Register: Registration <username><password>
                    Login: Login <username>
            """
            client.send(server_mess.encode('ascii'))
            
            user_command = client.recv(1024).decode('ascii')
            if user_command.split()[0] == "Registeration":
                message, first_time = register()
                client.send(message.encode('ascii'))
            elif user_command.split()[0] == "Login":
                message, first_time = login()
                client.send(message.encode('ascii'))
            else:
                print(f"Command {user_command} is not a valid one!")
                continue
        else:
            pass
    
        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            
            if password != 'adminpass':
                client.send(('REFUSE'.encode('ascii')))
                client.close()
                continue
            
        nicknames.append(nickname)
        clients.append(client)
        
        print(f"Nickname of client is {nickname}!")
        broadcast(f'{nickname} joined the chat!'.encode('ascii'))
        client.send("Connected to the server".encode('ascii'))
        
        thread = threading.Thread(target = handle, args = (client,))
        thread.start()
        
print("Server is listening...")
receive()