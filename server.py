import os
import re
import sys
import json
import struct
import socket
import sqlite3
import hashlib
import threading
from time import sleep
from hashlib import md5
from Crypto.Cipher import AES
from colorama import Fore
from tools.readConf import read_config
from Crypto.Random import get_random_bytes
from tools.Print_line import line_print
from tools.encryption import AESCipher

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
                response = encode_AES(key, response)
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
                # ct = encode_AES(key, message)
                # ct is str
                encoded_mess = encode_AES(key, message)
                # Send message length first
                client.sendall(struct.pack('!I', len(encoded_mess)))
                # Then send the message
                client.sendall(encoded_mess)
                
    def notify_join_to_all(self, current_client: socket, message: str):
        for client in self.active_client:
            if client != current_client:
                self.send_message_to_client(client[1], message)
                      
    def send_messages_to_all(self, message):
        for client in self.active_client:
            self.send_message_to_client(client[1], message)
            
    def send_messages_to_all_global(self, message: str):
        for client in self.active_client:
            client[1].sendall(message.encode())
    
    def register(self, username, password):
        self.db_con.execute("SELECT * FROM user WHERE username=?", (username,))
        result = self.db_con.fetchall()
        if result:
            return {"flag":"close", "message":"Username already exists, connect and try again"}
        else:
            self.db_con.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
            self.conn.commit()
            return {"flag":"close", "message":"you are successfully registered, connect again and login"}
            
    def login(self, username):
        self.db_con.execute("SELECT * FROM user WHERE username=?", (username,))
        result = self.db_con.fetchall()
        if result:
            # retrieve registered user password.
            self.db_con.execute("SELECT password FROM user WHERE username=? ", (username,))
            password = self.db_con.fetchall()
            
            # generate random key
            random_key = str(get_random_bytes(AES.block_size))
            
            # encrypt ranndom key with password and send it to user
            ciphertext = AESCipher(password[0][0]).encrypt(random_key).decode('utf-8')
            return {"flag": "login", "message":str(ciphertext)}, random_key
        else:
            return {"flag":"close", "message":"username or password is wrong!"}
    
    def broadcast(self, user, flag, user_message = None, users_list = None):
        if flag == "join":
            message = f"{user["username"]} has joined the chatroom!"
            target_users  = self.active_client
        if flag == "Public":
            target_users = self.active_client
            message = f"Public message from {user["username"]},{len(message)}:\r\n {user_message}\r\n"
        if flag == "Private":
            target_users = users_list
            message = f"Private message,{len(message)} from {user["username"]} to {users_list}\r\n{user_message}"
        
        for user in target_users:
            try:
                cipher_message = AESCipher(user["key"]).decrypt(message).decode('utf-8')
                user["conn"].send(cipher_message)
            except Exception as e:
                print("Error broadcasting message:", e)
                
    def setup_client_connection(self, client):
        while True:
            user_message = client.recv(1024).decode()
            # print("this is the user message: ", user_message)
            user_message = json.loads(user_message)
            print(Fore.BLACK, user_message)
            
            if user_message["flag"] == "register":
                message = self.register(user_message["username"], user_message["password"])
            elif user_message["flag"] == "login":
                message, random_key = self.login(user_message["username"])
            
            # Serialize the message dictionary into a JSON string
            json_data = json.dumps(message)
            # Send the JSON message over the socket
            client.sendall(bytes(json_data, encoding="utf-8"))
            
            # Check if the client sends a "Hello" message
            hello_message = client.recv(1024).decode()
            decrypted_hello = AESCipher(random_key).decrypt(hello_message).decode('utf-8')
            user = {
                    "conn":client,
                    "username":user_message["username"],
                    "password":user_message["password"],
                    "key":random_key
                }
            if decrypted_hello == "Hello":
                # broadcast user has joined the chat
                self.broadcast(user)
                # say weclome to the user
                welcome_message = f"Hi, {user_message["username"]} Welcome  to the chatroom!"
                client.sendall(welcome_message.encode())
                
                # add client to list of clients
                self.active_client.append(user)
                
                joining_leaving(f"{nickname} has joined the chatroom!".encode(), client)
                r=handle_chatroom_connection(client, addr)  # Handle chatroom connection here
                if r=="Goodbye.You are not allowed in the chatroom anymore":
                    break
            else:
                print("Client did not send 'Hello'")
            break
            
        # Decode the received data and split it into command and login data
            # try:
            #     # Deserialize the JSON message into a Python dictionary
            #     user_message = json.loads(user_message)
            #     print(user_message)
            # except ValueError:
            #     print("Invalid format of received data:", user_message)
            #     continue
            
            # # sends the result of user command to the client, whether registered or logged in.
            # message = self.handel_command(user_command)
            # if "invalid" in message:
            #     client.sendall(message.encode())
            # if "close" in message:
            #     client.sendall(message.encode())
            #     break
            # if "valid" in message:
            #     client.sendall(message.encode())
            #     username = user_command.split()[1]
            #     user_pass = user_command.split()[2]
            #     accept_mess = "[SERVER-public]" + "~" + f"{username} join the chat"
            #     welcome_mess = "[SERVER-private]" + "~" + f"{username} welcome to the chat"
            #     # key = encode_AES(get_random_bytes(16), password)
            #     # key = hashlib.sha256(key.encode()).digest()
            #     # generated_key = generate_key(user_pass)
                
            #     # Create a SHA-256 hash object
            #     hash_object = hashlib.sha256()
            #     # Convert the password to bytes and hash it
            #     hash_object.update(user_pass.encode())
            #     # Get the hex digest of the hash
            #     hash_password = hash_object.hexdigest()

            #     print("server generated:" + str(hash_password[:16]))
            #     self.active_client.append([username, client, user_pass, str(hash_password[:16]).encode()])
            #     self.notify_join_to_all(client, accept_mess)
            #     sleep(0.1)
            #     client.sendall(str(hash_password[:16]).encode())
            #     sleep(0.5)
            #     self.send_message_to_client(client, welcome_mess)
            #     threading.Thread(target = self.listen_for_messages, args = (client, )).start()      
            # else:
            #     client.close()
            #     continue
            # break
                
    # def handel_command(self, user_command: str) -> str:
    #     user_command = user_command.split()
    #     comm_type = user_command[0]
    #     username = user_command[1]
    #     password = user_command[2]
    #     message_type = ["invalid", "valid","close"]
        
    #     if ' ' in username:
    #         return f"{message_type[0]} username must not include white space"
    #     if ' ' in password:
    #         return f"{message_type[0]} password must not include white space"
        
    #     if comm_type == "Registration":
    #         self.db_con.execute("SELECT * FROM user WHERE username=?", (username,))
    #         result = self.db_con.fetchall()
    #         if result:
    #             message = f"{message_type[0]} Username already exists!"
    #         else:
    #             self.db_con.execute("INSERT INTO user (username, password) VALUES (?,?)", (username, password))
    #             self.conn.commit()
    #             message = f"{message_type[1]} you are successfully registered!"
    #     elif comm_type == "Login":
    #         self.db_con.execute("SELECT * FROM user WHERE username=? AND password=?", (username, password))
    #         result = self.db_con.fetchall()
    #         if result:
    #             message = f"{message_type[1]} You have Logged in successfully"
    #         else:
    #             message = f"{message_type[2]} username or password is wrong!"
    #     else:
    #         message = f"{message_type[0]} Your command is not a valid one"
    #     return message