import socket
import time
import struct
import threading
from time import sleep
from colorama import Fore
from tools.readConf import read_config
from tools.Print_line import line_print
from tools.encryption import aes_encode, aes_decode

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
    
    def listen_get_permission_from_server(self, client):
        while True:
            message = client.recv(2048).decode('utf-8') #
            if message != '':
                print(Fore.BLUE + message, end = '\n')
                line_print()
                client.sendall(input(Fore.WHITE + "write command: ").encode('utf-8')) #
                message = client.recv(2048).decode('utf-8')
                if "invalid" in message:
                    print(message.split()[1])
                    continue
                if "close" in message:
                    client.close()
                    print("client is closed")
                    break
                if "valid" in message:
                    print(" ".join(message.split()[1:]))
                    self.key = client.recv(2048)
                    print(f"KEY {self.key}")
                    threading.Thread(target= self.send_message_to_server , args=(client,)).start()
                    threading.Thread(target= self.recv_message_from_server , args=(client,)).start()
                    break 
            else:
                print(Fore.RED + 'Message has recieved from server is Empty, we are closing the client...')
                time.sleep(0.3)
                line_print()
                client.close()
                break
            
            
    def send_message_to_server(self, client): # send mesasage to the server when client Enter something 
        while 1:
            try:
                sleep(0.1)
                message = input("chat> ")
                if message != '':
                    ct = aes_encode(self.key, message)
                    client.sendall(ct.encode('utf-8'))
                else :
                    print(Fore.RED + "Message can not be empty")
                    line_print()
                    
            except:
                print(Fore.RED + "Something wrong happen in Entering Messages Chatroom stop")
                line_print()
                exit(0)
                
    def recv_message_from_server(self, client): # send mesasage to the server when client Enter something 
        while True:
            # try:
            message_length = struct.unpack('!I', client.recv(4))[0]
            # Then receive the actual message
            message = client.recv(message_length).decode('utf-8')
            print(aes_decode(self.key, message))
            # except:
                # print("An error occured!")
                # client.close()
                # break
        
    def commiunicate_to_server(self , client): # after client request for connecting make a connection to the server
        threading.Thread(target= self.listen_get_permission_from_server , args=(client,)).start()