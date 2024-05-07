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
        # Initialize the Client class with configurations from read_config() and a key attribute set to None
        self.configs = read_config()
        self.key = None
        
        
    def print_client_guide(self):
        # Method to print a guide for using the client's messaging features
        client_guide = """
        Messages can be sent in follwing format:
                1. Public normal message: 
                    <description: this message will be sent to everyone including urself>
                    <example:
                        Public message, length=<11>:
                        <Hello World>
                    >
                2. Private normal message:
                    <description: this message will be sent to the people you mention>
                    <example:
                        Private message, length=<11> to <Reza>,<user_name2>,<user_name3>:
                        <Hello World>
                    >
                3. Bye:
                    <description: this message command is used to quit the chatroom>
                    <example:
                         - Bye
                    >
                4. Guide doens't work right now
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
        """
            Builds a client connection to the server.

            Returns:
            socket.socket: The connected client socket.
        """
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
        """
        Creates a client session by handling user input and sending the appropriate message to the server.

        Args:
            client (socket.socket): The connected client socket.

        Returns:
            dict: The message dictionary containing the user's request.
        """
        entry_message = """
            HI, Sir/Mam; Please enter your choice in one of the following format:
            Register: Registration <username><password>
            Login: Login <username><password>
            Manual: -m
            """
        user_query = input(Fore.BLUE + entry_message)
        if user_query == "-m":
            self.print_client_guide()
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
        """
            Prompts the user to enter the "Hello" message and encrypts it using the generated key.

        Returns:
            tuple: A tuple containing the encrypted ciphertext and the initialization vector (IV).
        """
        message = input("say 'Hello' to join to the chatroom: ")
        if message.lower() == "hello":
            ciphertext, iv = AESCipher(self.key).encrypt(message.encode())
            return ciphertext, iv
        else:
            return False
        
        
    def receive_message_from_chatroom(self, client, username) -> None:
        """
        Receives and processes messages from the chatroom server.

        Args:
            client (socket.socket): The client socket connection to the chatroom server.
            username (str): The username of the client receiving messages.

        """
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
        """
        Encrypts and sends a message to the client.

        Args:
            message (str): The message to be sent.
            client (socket.socket): The client socket connection.

        This method encrypts the message using the AESCipher class and the encryption key, then sends the encrypted message to the client.
        """
    
        ciphered_message, iv = AESCipher(self.key).encrypt(message.encode())
        client.sendall(iv)
        sleep(0.1)
        client.sendall(ciphered_message)
    
    
    def send_message_to_chatroom(self, client) -> None:
        """
        Sends messages to the chatroom server.

        Args:
            client (socket.socket): The client socket connection to the chatroom server.

        This method prompts the user for input, sends messages to the server, and handles the 'Bye' flag to exit the chatroom.
        """
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
        """
        Receives and decrypts a message from the client.

        Args:
            client (socket.socket): The client socket connection.

        Returns:
            str: The decrypted message.

        This method receives an encrypted message from the client, decrypts it using the AESCipher class and the encryption key, and returns the decrypted message.
        """
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
        """
        Establishes communication with the server after client connection.

        Args:
            client (socket.socket): The connected client socket.

        This method handles the communication process with the server after the client connects.
        It creates a client session, receives server messages, processes login information, handles the initial handshake, and starts threads for sending and receiving messages in the chatroom.
        """
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