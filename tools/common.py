import os
import json

def check_white_space(txt: str) -> bool:
    return ' ' in txt

def extract_username_password(user_query: str) -> str:
    username = user_query.split('<')[1].split('>')[0]
    password = user_query.split('<')[2].split('>')[0]
    return username, password

def extend_to_16_bytes(input_string):
    """
    Extends the input string to 16 bytes by padding it with null characters.
    
    Args:
        input_string (str): The input string to be extended.
        
    Returns:
        bytes: The extended byte array with a length of 16 bytes.
    """
    print(type(input_string))
    # Convert the input string to bytes
    byte_array = input_string.encode('utf-8')
    
    # Pad the byte array to 16 bytes
    if len(byte_array) < 16:
        padding_length = 16 - len(byte_array)
        byte_array += b'\x00' * padding_length
    
    return byte_array


def receive_file(conn, file, save_directory):
    try:
        file_info = file["file"]
        file_name = file_info["filename"]
        file_size = int(file_info["filesize"])
        file_path = os.path.join(save_directory, file_name)
        
        with open(file_path, "wb") as file:
            received_size = 0
            while received_size < file_size:
                data = conn.recv(1024)
                file.write(data)
                received_size += len(data)
            print(f"File '{file_path}' received successfully.")
            
    except Exception as e:
        print(f"An error occurred while receiving the file '{file_name}':", e)
        
def make_portable(obj: any) -> bytes:
    json_data = json.dumps(obj)
    return bytes(json_data, encoding="utf-8")

def make_usable(obj: json) -> bytes:
    return json.loads(obj)