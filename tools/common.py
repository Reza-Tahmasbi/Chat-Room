import os
import json

def check_white_space(txt: str) -> bool:
    """
    Check if a string contains any white spaces.

    Args:
        txt (str): The string to be checked.

    Returns:
        bool: True if the string contains any white spaces, False otherwise.
    """
    return ' ' in txt


def extract_username_password(user_query: str) -> tuple:
    """
    Extract the username and password from a user query string.

    Args:
        user_query (str): The user query string in the format "Registration <username><password>".

    Returns:
        tuple: A tuple containing the extracted username and password.
    """
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
    """
    Receive and save a file from the connection.

    Args:
        conn (socket.socket): The connection socket.
        file (dict): The file information dictionary.
        save_directory (str): The directory to save the file.

    This function receives a file from the connection, saves it to the specified directory, and prints a success message upon completion.
    """
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
    """
    Convert an object to a portable byte representation.

    Args:
        obj (any): The object to be converted.

    Returns:
        bytes: The byte representation of the object.
    """
    json_data = json.dumps(obj)
    return bytes(json_data, encoding="utf-8")


def make_usable(obj: json) -> bytes:
    """
    Convert a JSON object to bytes.

    Args:
        obj (json): The JSON object to be converted.

    Returns:
        bytes: The byte representation of the JSON object.
    """
    return json.loads(obj)