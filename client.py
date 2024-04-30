import json
import time
import socket
import struct
import threading
from time import sleep
from colorama import Fore
from tools.commands import *
from tools.readConf import read_config
from Crypto.Protocol.KDF import PBKDF2
from tools.Print_line import line_print
from tools.encryption import AESCipher

class Client():
    def __init__(self):
        self.configs = read_config()
        self.key = None
        
    def build_connection(self):
        client = client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            client.connect((self.configs['HOST'] , self.configs['PORT']))
            print(Fore.GREEN + 'Client has connected to the server successfuly')
            line_print()
        except:
            print(Fore.RED + f"Client can not be connected to {self.configs['HOST']}")
            line_print()
        return client
    
    def create_client(self, client):
        entry_message = """
        
            HI, Sir/Mam; Please enter your choice in one of the following format:
            Register: Registration <username><password>
            Login: Login <username><password>
            
            """
        user_query = input(Fore.BLUE + entry_message)
        try:
            # extract username and password
            username, password = extract_username_password(user_query)
            
            # check for white space before registration process.
            if check_white_space(username) or check_white_space(password):
                print("There is a white space in either password or username!")
                return self.create_client(client)
                
            # setup the flag for operation on server (register/login)
            if "Registration" in user_query:
                message = {"flag":"register",
                            "username": username,
                            "password": password}
            
            elif "Login" in user_query:
                message = {"flag":"login",
                            "username": username,
                            "password": password}
                
            # Serialize the message dictionary into a JSON string
            json_data = json.dumps(message)

            # Send the JSON message over the socket
            client.sendall(bytes(json_data,encoding="utf-8"))
            
        except:
            print(Fore.RED + "Invalid Request")
            return self.create_client(client)
        return message
    
    # def listen_get_permission_from_server(self, client):
    #     while True:
    #         message = client.recv(2048).decode() #
    #         if message != '':
    #             print(Fore.BLUE + message, end = '\n')
    #             line_print()
    #             client.sendall(input(Fore.WHITE + "write command: ").encode()) #
    #             message = client.recv(2048).decode()
    #             if "invalid" in message:
    #                 print(message.split()[1])
    #                 continue
    #             if "close" in message:
    #                 client.close()
    #                 print("client is closed")
    #                 break
    #             if "valid" in message:
    #                 print(" ".join(message.split()[1:]))
    #                 # self.key = client.recv(32)
    #                 self.key = client.recv(1024)
    #                 print(self.key)
    #                 print(f"KEY {str(self.key)}")
    #                 threading.Thread(target= self.send_message_to_server , args=(client,)).start()
    #                 threading.Thread(target= self.recv_message_from_server , args=(client,)).start()
    #                 break 
    #         else:
    #             print(Fore.RED + 'Message has recieved from server is Empty, we are closing the client...')
    #             time.sleep(0.3)
    #             line_print()
    #             client.close()
    #             break
            
            
    # def send_message_to_server(self, client): # send mesasage to the server when client Enter something 
    #     while 1:
    #         try:
    #             sleep(0.1)
    #             message = input("chat> ")
    #             if message != '':
    #                 ct = encode_AES(self.key, message)
    #                 client.sendall(ct.encode())
    #             else :
    #                 print(Fore.RED + "Message can not be empty")
    #                 line_print()
                    
    #         except:
    #             print(Fore.RED + "Something wrong happened in Entering Messages Chatroom stop")
    #             line_print()
    #             exit(0)
                
    # def recv_message_from_server(self, client): # send mesasage to the server when client Enter something 
    #     while True:
    #         # try:
    #         message_length = struct.unpack('!I', client.recv(4))[0]
    #         # Then receive the actual message
    #         message = client.recv(message_length).decode()
    #         print(decode_AES(self.key, message))
    #         # except:
    #             # print("An error occured!")
    #             # client.close()
    #             # break

    def hello_message(self):
        message = input("say 'Hello' to join to the chatroom: ")
        if message.lower() == "hello":
            ciphertext = AESCipher(self.key).encrypt(message).decode('utf-8')
            return ciphertext
        else:
            return False
        
    def commiunicate_to_server(self , client): # after client request for connecting make a connection to the server
        # threading.Thread(target= self.create_client , args=(client,)).start()
        user_data = self.create_client(client)
        print(user_data)
        
        server_message = client.recv(1024).decode()
        print("server_message", server_message)
        server_message = json.loads(server_message)
        # print(server_message)
        
        if server_message["flag"] == "close":
            print(server_message["message"])
            client.close()
            
        else: # when the flag is login
            # take the encrypted random key and decode it
            print("Key", server_message["message"] + "\n")
            self.key = AESCipher(user_data["password"]).decrypt(server_message["message"]).decode('utf-8')
            # handle hello operation
            result = self.hello_message()
            if result:
                client.sendall(result)
                server_message = client.recv(1024).decode()
                print(server_message)
            else:
                print("You did not say hello, so have a good day!")
                client.close()
            
        print("[Connection has been closed]")
        
        