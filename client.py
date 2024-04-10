import socket
import threading
from tools.readConf import read_config
from time import sleep
from colorama import Fore , Back
from tools.Print_line import line_print

class Client():
    def __init__(self):
        self.configs = read_config()
        
    def build_connection(self):
        client = client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try :
            client.connect((self.configs['HOST'] , self.configs['PORT']))
            print(Fore.RED + 'Client has connected to the server succesfuly')
            line_print()
        except:
            print(Fore.RED + f"Client can not be connected to {self.configs['HOST']}")
            line_print()
        return client
    
    
    def listen_for_messages_from_server(self, client):
        while True:
            message = client.recv(2048).decode('utf-8')
            if message != '':
                print(Fore.YELLOW + message, end = '\n')
                line_print()
                client.sendall(input("write command: ").endcode('utf-8'))
            else:
                print(Fore.RED + 'Message has recieved from server is empty')
                line_print()
                break
            
            
    def send_message_to_server(self, client): # send mesasage to the server when client Enter something 
        while 1:
            try:
                sleep(0.5)
                message = input()
                if message != '':
                    client.sendall(message.encode('utf-8'))
                else :
                    print(Fore.RED + "Message can not be empty")
                    line_print()
                    
            except:
                print(Fore.RED + "Something wrong happen in Entering Messages Chatroom stop")
                line_print()
                exit(0)
        
        
    def commiunicate_to_server(self , client  , username): # after client request for connecting make a connection to the server
        # username = input("Enter Your Username : ")
        # if username != '':

        # client.sendall(username.encode('utf-8'))
        # print(Fore.RED + "Client sent username to the server")
        # line_print()
        
        # else :
        #     print("Username can not be empty")
        #     exit(0)
        
        threading.Thread(target= self.listen_for_messages_from_server , args=(client,)).start()
        self.send_message_to_server(client)
        
        
# def recieve():
#     while True:
#         try:
#             message = client.recv(1024).decode('ascii')
#             print(message)
#             if message == "mode":
#                 user_input =    
#                 client.send("ask: ".endcode('ascii'))
#             else:
#                 print(message)
#         except:
#             print("An error occured!")
#             client.close()
#             break

# def write():
#     while True:
#         message = f'{nickname}: {input("")}'
#         client.send(message.encode("ascii"))
        
        
# client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# client.connect(('127.0.0.1', 15000))

# print("Welcome to your pleasent Chat Room")
# while True:
#     user_input = input("ask: ")
#     if user_input.split()[0] == "Registeration":
#         register(user_input)
#         break
#     elif user_input.split()[0] == "Login":
#         login(user_input)
#         break
#     else:
#         print(f"Command {user_input} is not a valid one!\nRegister: Registration <username><password>\nLogin: Login <username>")
    
    
# recieve_thread = threading.Thread(target = recieve)
# recieve_thread.start()

# write_thread = threading.Thread(target = write)
# write_thread.start()
