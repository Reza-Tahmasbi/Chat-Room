import threading
from server import Server
from colorama import Fore
from tools.Print_line import line_print

def start():
    server_init = Server()
    server = server_init.build_server()
    server.listen(server_init.configs['TIME_OUT'])
    
    while 1:
        client, address = server.accept()
        server_mess = """
        Register: Registration <username><password>
        Login: Login <username>
        """
        client.send(server_mess.encode('ascii'))
        user_command = client.recv(1024).decode('ascii')
        if user_command.split()[0] == "Registeration":
            message = register()
            client.send(message.encode('ascii'))
        elif user_command.split()[0] == "Login":
            message, status = login()
            client.send(message.encode('ascii'))
            if status == True:
                ct = aes_encode(get_random_bytes(16), password)
                client.send(f"KEY {ct}".encode('ascii'))
        else:
            message = f"Command {user_command} is not a valid one!"
            client.send(message.encode('ascii'))
            client.close()
            continue
        print(Fore.RED + f"Successfully connected to client {address[0]} {address[1]}")
        line_print()
        server_mess = """
        Register: Registration <username><password>
        Login: Login <username>
        """
        threading.Thread(target=server_init.client_handler, args=(client, )).start()
        
if __name__ == '__main__':
    start()