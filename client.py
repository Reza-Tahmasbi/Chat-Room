import socket
import threading
from time import sleep
from colorama import Fore
from tools.common import *
from tools.message import *
from tools.encryption import AESCipher
from tools.readConf import read_config
from tools.Print_line import line_print
from tools.encryption import generate_key

class Client():
    def __init__(self):
        self.configs = read_config()
        self.key = None
        
    def print_client_guide(self):
        client_guide = """
        Messages can be sent in follwing format:
                1. Public normal message: 
                    <description: this message will be sent to everyone including urself>
                    <example:
                        Public message, length=<message_len>:
                        <message_body>
                    >
                2. Private normal message:
                    <description: this message will be sent to the people you mention>
                    <example:
                        Private message, length=<message_len> to <user_name1>,<user_name2>,<user_name3>:
                        <message_body>
                    >
                3. Bye:
                    <description: this message command is used to quit the chatroom>
                    <example:
                         - Bye
                    >
                4. Guide
                    <description: this command prints this message :)>
                    <example:
                        - Guide
                    >
                    
                tags:
                    <file: You can send a file with message using 'file' tag.>
                    <bold: You can send bold message using 'bold' tag.>
                    <italic: You can send italic message using 'italic' message.>
                    <underline: You can send 'underlined' message using 'underline' tag.>
                    <highlight: You can send highlightened message using highlight tag.>
                tips:
                    links will be highlightened automatically
        """
        
        print(client_guide)
        
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
                
            # Send message as json file
            client.sendall(make_portable(message))
            
        except:
            print(Fore.RED + "Invalid Request")
            return self.create_client(client)
        return message
    
    def hello_message(self):
        message = input("say 'Hello' to join to the chatroom: ")
        if message.lower() == "hello":
            ciphertext, iv = AESCipher(self.key).encrypt(message.encode())
            return ciphertext, iv
        else:
            return False
        
    def receive_message_from_chatroom(self, client, username) -> None:
        save_directory = os.getcwd()
        os.makedirs(os.path.join(save_directory, username), exist_ok=True)
        while True:
            try:
                # Receive messages from the server
                message = self.receive_message(client)
                message = process_message(message)
                if message:
                    print("[Server]:", message["message"])
                    if "file" == message["flag"]:
                        receive_file(client, username, message["file"], os.join(save_directory, username))
            except Exception as e:
                print("An error occurred while receiving messages:", e)            
           
    def send_message(self, message, client):
        ciphered_message, iv = AESCipher(self.key).encrypt(message.encode())
        client.sendall(iv)
        sleep(0.1)
        client.sendall(ciphered_message)
    
    def send_message_to_chatroom(self, client) -> None:
        while True:
            try:
            # Prompt for user input and send messages to the server
                sleep(0.2)
                user_message = str(input("\nYou> "))
                message_info = process_message(user_message)
                self.send_message(message_info["message"], client)
                if message_info["flag"] == 'Bye':
                    print("You left the chat")
                    break
            except Exception as e:
                print("An error occurred while sending messages:", e)
                
    def receive_message(self, client):
        iv = client.recv(1024)
        sleep(0.2)
        message = client.recv(1024)
        try:
            if message["flag"] == "close":
                print(message["message"])
                client.close()
                return None
        except:
            decrypted_hello = AESCipher(self.key).decrypt(message, iv).decode()
        return decrypted_hello
        
    def commiunicate_to_server(self , client): # after client request for connecting make a connection to the server
        user_data = self.create_client(client)
        # re2
        server_message = client.recv(1024).decode()
        server_message = make_usable(server_message)
        line_print()
        if server_message["flag"] == "close":
            print(server_message["message"])
            client.close()
            
        else: # when the flag is login
            # take the encrypted random key and decode it
            print("Key", server_message["body"] + "\n")
            line_print()
            self.key = generate_key(user_data["password"], server_message["body"]).encode()
            # handle hello operation
            result, iv = self.hello_message()
            if result:
                client.sendall(iv)
                sleep(0.2)
                client.sendall(result)
                sleep(0.2)
                message = self.receive_message(client)
                server_message = process_message(message)
                # welcome message being printed
                print(server_message["message"])
                print(f"You can now chat here")
                
                # prints an overall giude for user.
                receive_message_thread = threading.Thread(target=self.receive_message_from_chatroom, args=(client,user_data["username"]))
                send_message_thread = threading.Thread(target=self.send_message_to_chatroom, args=(client,))
                receive_message_thread.start()
                send_message_thread.start()
                receive_message_thread.join()
                send_message_thread.join()
            else:
                # if not saying hello, then we close the connection
                print("You did not say hello, so have a good day!")
                client.close()
            
            
        print("[Connection has been closed]")