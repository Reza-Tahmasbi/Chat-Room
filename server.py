import sys
import socket
import sqlite3
import threading
from time import sleep
from colorama import Fore
from tools.common import *
from tools.message import * 
from tools.history import History
from tools.readConf import read_config
from tools.encryption import AESCipher
from tools.Print_line import line_print
from tools.encryption import generate_key
from Crypto.Random import get_random_bytes

class Server:
    def __init__(self):
        # user [conn, username, password, client]
        self.active_client = []
        self.configs = read_config()
        self.conn = sqlite3.connect('database.db', check_same_thread=False)
        self.db_con = self.conn.cursor()
        self.history = History()
        
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
        
    def broadcast(self, message, target_users = None):
        for user in target_users:
            ciphertext, iv = AESCipher(user["key"]).encrypt(message.encode())
            user["conn"].sendall(iv)
            sleep(0.2)
            user["conn"].sendall(ciphertext)
             
    def receive_message(self, client, user):
        iv = client.recv(1024)
        sleep(0.1)
        message = client.recv(1024)
        decrypted_hello = AESCipher(user["key"]).decrypt(message, iv).decode()
        return decrypted_hello
       
    def chatroom_handel(self, user):
        client = user["conn"]
        while True:
            try:
                user_message_decoded = self.receive_message(client, user)
            except:
                print(Fore.RED + f"Client has left or sent a wrong command")
                line_print()
                break
            try:
                message_info = process_message(user_message_decoded)
                if message_info["flag"] not in ("Please","Private","Bye","Public"):
                    server_message = "Message Not Valid! Enter the correct message:"
                    self.broadcast(server_message, [user])
                else:
                    if message_info["flag"] == "Please":
                        server_message = list_names_from_server(self.active_client)
                        print(server_message)
                        self.broadcast(server_message, [user])
                        
                    elif message_info["flag"] == "Public":
                        server_message = public_from_server(message_info)
                        self.broadcast(server_message, self.active_client)
                        
                    elif message_info["flag"] == "Private":
                        server_message = list_names_from_server(message_info)
                        self.broadcast(server_message, message_info["usernames"])
                        
                    elif message_info["flag"] == "Bye" or client.close():
                        server_message = bye_to_server(message_info)
                        self.broadcast(server_message, self.active_client)
                        self.active_client.remove(user)
                        
            except Exception as e:
                print("Error broadcasting message:", e)
    
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
            salt = str(get_random_bytes(32))
            generated_key = generate_key(password[0][0], salt).encode()
            return process_message("login " + salt), generated_key
        else:
            return process_message("close username or password is wrong!")
    
    def check_if_already_logged_in(self, user_message):
        for user in self.active_client:
            if user_message['username'] == user['username']:
                self.active_client.remove(user)
                
    def setup_client_connection(self, client):
        while True:
            user_message = client.recv(1024).decode()
            user_message = make_usable(user_message)
            print(user_message)
            
            if user_message["flag"] == "register":
                message = self.register(user_message['username'], user_message["password"])
            elif user_message["flag"] == "login":
                message, generated_key = self.login(user_message['username'])
            
            client.sendall(make_portable(message))
            
            # Check if the client sends a "Hello" message
            iv = client.recv(1024)
            sleep(0.2)
            hello_message = client.recv(1024)
            try:
                decrypted_hello = AESCipher(generated_key).decrypt(hello_message, iv).decode()
            except:
                client.sendall("close Your password is wrong! try again.".encode())
                break
            
            user = {
                    "conn":client,
                    'username':user_message['username'],
                    "password":user_message["password"],
                    "key": generated_key
                }
            
            if decrypted_hello == "Hello":
                # check if user is already in the chatroom, then we remove old one.
                self.check_if_already_logged_in(user_message)
                # broadcast to all that user has joined the chat
                message = f"{user['username']} has joined the chatroom!"
                self.broadcast(message, self.active_client)
                # say weclome to the specific user
                sleep(0.2)
                welcome_message = f"Hi, {user_message['username']} Welcome to the chatroom!"
                self.broadcast(welcome_message, [user])
                # add client to list of clients
                self.active_client.append(user)
                # notify a new member has arrived.

                # guide user into the chatroom
                # chatroom_response = self.chatroom_handel(user)  # Handle chatroom connection here
                threading.Thread(target=self.chatroom_handel, args=(user,)).start()
                # if chatroom_response=="Goodbye.You are not allowed in the chatroom anymore":
                #     break
            else:
                print("Client did not send 'Hello'")
            break
            