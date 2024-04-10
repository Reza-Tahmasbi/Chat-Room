from client import Client

def start(username): # start connecting client 
    try:
        x = Client()
        client = x.build_connection()
    except:
        raise Exception
    
    x.commiunicate_to_server(client , username)

if __name__ == '__main__':
    start("salam2")
