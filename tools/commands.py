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