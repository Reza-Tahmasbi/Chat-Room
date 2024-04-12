from client import Client

def start(): # start connecting client 
    try:
        x = Client()
        client = x.build_connection()
    except:
        raise Exception
    
    x.commiunicate_to_server(client)

if __name__ == '__main__':
    start()
