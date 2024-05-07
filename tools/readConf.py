import json 

def read_config():
    # Read configuration like Host name and Port number
    with open('configs/main.json') as file:
        data = json.load(file)
        return data