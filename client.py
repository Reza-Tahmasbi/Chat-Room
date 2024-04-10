import threading
import socket

    
def recieve():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            print(message)
            if message == "mode":
                user_input = input("ask: ")

            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break

def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode("ascii"))
        
        
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 15000))

print("Welcome to your pleasent Chat Room")
while True:
    user_input = input("ask: ")
    if user_input.split()[0] == "Registeration":
        register(user_input)
        break
    elif user_input.split()[0] == "Login":
        login(user_input)
        break
    else:
        print(f"Command {user_input} is not a valid one!\nRegister: Registration <username><password>\nLogin: Login <username>")
    
    
recieve_thread = threading.Thread(target = recieve)
recieve_thread.start()

write_thread = threading.Thread(target = write)
write_thread.start()
