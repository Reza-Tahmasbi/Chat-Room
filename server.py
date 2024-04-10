import re
import sys
import base64
import socket
import sqlite3
import threading
from time import sleep
from colorama import Fore
from Crypto.Cipher import AES
from tools.readConf import read_config
from tools.Print_line import line_print
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class Server:
    def __init__(self):
        self.active_client = []
        self.configs = read_config()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        self.db = c
        
    def build_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((self.configs['HOST'], self.configs['PORT']))
            print(Fore.GREEN + f"Connected successfully server:{self.configs['HOST']}")
            line_print()
        except:
            print(Fore.RED + f"Unable Run the server on {self.configs['HOST']}")
            line_print()
            sys.exit(0)
            
        return server
        
    def listen_for_messages(self, client, username):
        while True:
            try:
                response = client.recv(2048).decode('utf-8')
            except:
                print(Fore.RED + f"Client has left or sent a wrong command")
                line_print()
                break
            splited_response = response.split(' ')
            
            if splited_response[0] not in ("Please","Private","Bye","Public"):
                final_message = "Enter Correct message"
                self.send_message_to_client(client, final_message)
            else:

                if splited_response[0] == "Please":
                    final_message = '[Server]' + f"Here is the list of attendees: {[(f'<{username_[0]}>') for username_ in self.active_client]} "    
                    self.send_message_to_client(client, final_message)
                elif splited_response[0] == "Public":
                    content = re.findall(r'<(.*?)>', response)
                    final_message ='[Server]' +  f"Public message from <{username}>, length=<{content[0]}>: \n\r <{content[1]}>"
                    self.send_messages_to_all(final_message)
                elif splited_response[0] == "Private":
                    content = re.findall(r'<(.*?)>', response)
                    final_message ='[Server]' +  f"Private message, length=<{content[0]}> from <{username}> to {[(f'<{username_}>') for username_ in content[1:-1]]}: <{content[-1]}>"
                    self.send_messages_to_all(final_message)
                elif splited_response[0] == "Bye" or client.close():
                    final_message ='[Server]' +  f"<{username}> left the chat room."
                    self.send_messages_to_all(final_message)
                    self.active_client.remove((username , client))
                    
    def send_message_to_client(self, client, message):
        client.sendall(message.encode('utf-8'))
           
    def send_messages_to_all(self, message):
        for client in self.active_client:
            self.send_message_to_client(client[1], message)
        
    def client_handler(self, client):
        while True:
            server_mess = """
            Register: Registration <username><password>
            Login: Login <username>
            """
            client.sendall(server_mess(2048).encode('utf-8'))
            user_command = client.recv(2048).decode('utf-8')
            # sends the result of user command to the client, whether registered or logged in.
            message = handel_command(user_command, client)
            for value in dict.values():
                print(value)
            client.send(value.encode("utf-8"))
            if "close" in message:
                client.close()
            if "valid" in message:
                ct = aes_encode(get_random_bytes(16), user_command.split()[2])
                client.send(f"KEY {ct}".encode('utf-8'))
            else:
                client.close()
                continue
            
            username = client.recv(2048).decode('utf-8')
            if username != '':
                self.active_client.append((username, client))
                correct_message = "[SERVER-public]" + "~" + f"{username} join the chat"
                correct_message_private = "[SERVER-private]" + "~" + f"{username} welcome to the chat"
                self.send_messages_to_all(correct_message)
                sleep(1)
                self.send_message_to_client(client, correct_message_private)
                break
            else:
                print(Fore.RED + "There is Problem in client handling")
                line_print()
                
        threading.Thread(target = self.listen_for_messages, args = (client, username)).start()      

    
# handling client, constantly trying to get message from client
# as soon as client casued any error, it means the client has left the chat
# and we are going to remove it from our server
    
# def handle(client):
#     while True:
#         try:
#             message = client.recv(1024)
#             broadcast(message)
#         except:
#             index = clients.index(client)
#             clients.remove(client)
#             client.close()
#             nickname = nicknames[index]
#             broadcast(f'{nickname} left the chat!'.encode('ascii'))
#             nicknames.remove(nickname)
#             break

def handel_command(user_command: str, client: socket, conn) -> str:
    user_command = user_command.split()
    comm_type = user_command[0]
    username = user_command[1]
    password = user_command[2]
    
    if ' ' in username:
        return {"invalid": "username must not include white space"}#
    if ' ' in password:
        return {"invalid": "password must not include white space"}#
    
    if comm_type == "Register":
        conn.execute("SELECT * FROM user WHERE username=?", (username,))
        result = conn.fetchall()
        if result:
            message = {"invalid": "Username already exists!"}#
        else:
            conn.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
            conn.commit()
            message = {"valid": "You are successfully Registered!"}#
        client.send(message.encode('utf-8'))
        
    elif comm_type == "Login":
        conn.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
        result = conn.fetchall()
        if result:
            message = {"valid": "You have Logged in successfully"}#
        else:
            message = {"close": "username or password are wrong!"}
    else:
        message = {"invalid": "Your command is not a valid one"} #
    
    return message

def login(username: str, password: str, client: socket) -> str:
    if ' ' in username:
        return "username must not include white space"
    if ' ' in password:
        return "password must not include white space"
    results = c.execute("SELECT * FROM user WHERE username=?", (username,))
    results = c.fetchall()
    if results:
        message = "username already exists!"
    else:
        c.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
        conn.commit()
        message = "You are successfully Registered!"
    client.send(message.encode('ascii'))

def aes_encode(message: str, key: bytes) -> str:
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(message.encode('utf-8'), AES.block_size))
    ct = base64.b64encode(cipher.iv + ct_bytes).decode('utf-8')
    return ct

def aes_decode(ct: str, key: bytes) -> str:
    ct = base64.b64decode(ct)
    iv = ct[:16]
    ct = ct[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size).decode('utf-8')
    return pt

def receive():
    while True:
        client, address = server.accept()
        print(f"Connected with {str(address)}")
        
        server_mess = """
                Register: Registration <username><password>
                Login: Login <username>
        """
        client.send(server_mess.encode('ascii'))
        user_command = client.recv(1024).decode('ascii')
        
        ct = aes_encode(get_random_bytes(16), password)
        client.send(f"KEY {ct}".encode('utf-8'))
            
        if status == True:
            ct = aes_encode(get_random_bytes(16), password)
            client.send(f"KEY {ct}".encode('ascii'))

    
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