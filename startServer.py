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
        print(Fore.RED + f"Successfully connected to client {address[0]} {address[1]}")
        line_print()
        server_init.setup_client_connection(client)
        # threading.Thread(target=server_init.setup_client_connection, args=(client, )).start()
        
if __name__ == '__main__':
    start()