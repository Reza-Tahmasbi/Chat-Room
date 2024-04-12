import re
import sys
import socket
import sqlite3
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
        print("test_1")
        for c in self.active_client:
            if client in c:
                username = c[0] 
        while True:
            print("test_2")
            try:
                key = self.find_client_key(client)
                response = client.recv(2048).decode('utf-8')
                response = aes_encode(key, response)
                
                print("test_3")
            except:
                print(Fore.RED + f"Client has left or sent a wrong command")
                line_print()
                break
            splited_response = response.split(' ')
            print("test_4")
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
                    self.active_client.remove([username , client])
                
    def find_client_key(self, client):
        for c in self.active_client:
            if client in self.active_client:
                key = c[3]
        return key
    
    
    def send_message_to_client(self, client, message):
                key = self.find_client_key(client)
                ct = aes_encode(key, message)
                client.sendall(ct.encode('utf-8'))
           
    def send_messages_to_all(self, message):
        for client in self.active_client:
            self.send_message_to_client(client[1], message)
        
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
                username = user_command.split()[1]
                password = user_command.split()[2]
                ct = aes_encode(get_random_bytes(16), user_command.split()[2])
                self.active_client.append([username, client, password, ct])
                client.sendall(f"valid KEY {ct} {message}".encode('utf-8'))
                threading.Thread(target = self.listen_for_messages, args = (client, )).start()      
            else:
                client.close()
                continue
                
            username = user_command.split()[1]
            correct_message = "[SERVER-public]" + "~" + f"{username} join the chat"
            correct_message_private = "[SERVER-private]" + "~" + f"{username} welcome to the chat"
            try:
                self.send_messages_to_all(correct_message)
                sleep(1)
                self.send_message_to_client(client, correct_message_private)
            except:
                pass
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