import re
import sys
import struct
import socket
import sqlite3
import hashlib
import threading
from time import sleep
from colorama import Fore
from tools.readConf import read_config
from Crypto.Random import get_random_bytes
from tools.Print_line import line_print
from tools.encryption import aes_encode, aes_decode

class Server:
    def __init__(self):
        # [username, client, password, ct]
        self.active_client = []
        self.configs = read_config()
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.db_con = self.conn.cursor()
        
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
        
    def listen_for_messages(self, client):
        for c in self.active_client:
            if client in c:
                username = c[0] 
        while True:
            try:
                key = self.find_client_key(client)
                response = client.recv(1024)
                response = aes_decode(key, response)
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
                    final_message = '[Server]' + f"Here is the list of attendees: {[(f'<{user[0]}>') for user in self.active_client]} "    
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
                    self.active_client.remove([username , client])
                
    def find_client_key(self, client):
        for row in self.active_client:
            if client in row:
                key = row[3]
        return key
    
    def send_message_to_client(self, client, message):
                key = self.find_client_key(client)
                ct = aes_encode(key, message)
                # ct is str
                message = ct.encode("utf-8")
                # Send message length first
                client.sendall(struct.pack('!I', len(message)))
                # Then send the message
                client.sendall(message)
                
    def notify_join_to_all(self, current_client: socket, message: str):
        for client in self.active_client:
            if client != current_client:
                self.send_message_to_client(client[1], message)
                      
    def send_messages_to_all(self, message):
        for client in self.active_client:
            self.send_message_to_client(client[1], message)
            
    def send_messages_to_all_global(self, message: str):
        for client in self.active_client:
            client[1].sendall(message.encode("utf-8"))
        
    def grant_permission_client(self, client):
        while True:
            server_mess = """
            Register: Registration <username><password>
            Login: Login <username>
            """
            client.sendall(server_mess.encode('utf-8'))
            user_command = client.recv(2048).decode('utf-8')
            if user_command == '':
                break
            # sends the result of user command to the client, whether registered or logged in.
            message = self.handel_command(user_command)
            if "invalid" in message:
                client.sendall(message.encode("utf-8"))
            if "close" in message:
                client.sendall(message.encode("utf-8"))
                break
            if "valid" in message:
                client.sendall(message.encode('utf-8'))
                username = user_command.split()[1]
                password = user_command.split()[2]
                accpetance_message = "[SERVER-public]" + "~" + f"{username} join the chat"
                accpetance_message_private = "[SERVER-private]" + "~" + f"{username} welcome to the chat"
                key = aes_encode(get_random_bytes(16), user_command.split()[2])
                key = hashlib.sha256(key.encode()).digest()
                print("server generated:" + str(key))
                self.active_client.append([username, client, password, key])
                self.notify_join_to_all(client, accpetance_message)
                sleep(0.1)
                client.sendall(key)
                sleep(0.1)
                self.send_message_to_client(client, accpetance_message_private)
                threading.Thread(target = self.listen_for_messages, args = (client, )).start()      
            else:
                client.close()
                continue
            break
                
    def handel_command(self, user_command: str) -> str:
        user_command = user_command.split()
        comm_type = user_command[0]
        username = user_command[1]
        password = user_command[2]
        message_type = ["invalid", "valid","close"]
        
        if ' ' in username:
            return f"{message_type[0]} username must not include white space"
        if ' ' in password:
            return f"{message_type[0]} password must not include white space"
        
        if comm_type == "Registration":
            self.db_con.execute("SELECT * FROM user WHERE username=?", (username,))
            result = self.db_con.fetchall()
            if result:
                message = f"{message_type[0]} Username already exists!"
            else:
                self.db_con.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
                self.conn.commit()
                message = f"{message_type[1]} you are successfully registered!"
        elif comm_type == "Login":
            self.db_con.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
            result = self.db_con.fetchall()
            if result:
                message = f"{message_type[1]} You have Logged in successfully"
            else:
                message = f"{message_type[2]} username or password is wrong!"
        else:
            message = f"{message_type[0]} Your command is not a valid one"
        return message