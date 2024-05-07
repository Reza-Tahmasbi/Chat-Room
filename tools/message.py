import re
from colorama import Fore
    
class Styling:
    colors = {
        "Warning": Fore.YELLOW,
        "Success": Fore.GREEN,
        "System": Fore.LIGHTWHITE_EX,
        "Client": Fore.LIGHTCYAN_EX,
        "link": Fore.MAGENTA
    } 
        
def process_message(message, sender = "Server") -> None:
    info = {
        "flag":None,
        "message":message,
        "username": sender,
        "length":None,
        "body":None,
        "styling":None,
        "usernames":None
    }
    flag = re.search(r'(\w+)', message).group(1)
    info["flag"] = flag
    if flag.lower() == "login" or flag.lower() == "close":
        info["body"] = message.split(" ")[1]
    else:
        info["body"] = message
    if flag.lower() == "private" or flag.lower() == "public":
        info["length"] = re.search('length=<(\d+)>', message).group(1)
        info["body"] = re.search(':<(.+)>', message).group(1)
        
        if flag.lower() == "private":
            message = message.split("to")[1].split(":")[0]
            info["usernames"] = re.findall(r'<(\w+)>', message)
    return info

def public_from_server(info: dict) -> str:
    return f"Public message from <{info['username']}>, length=<{info['length']}>:<{info['body']}>\n"
    
def private_from_server(info: dict) -> str:
    return f"Private message, length=<{info['length']}> from <{info['username']}> to {','.join([(f'<{username_}>') for username_ in info['usernames']])}:<{info['body']}>\n"
        
def list_names_from_server(users: list) -> str:
    usernames = []
    for user in users:
        usernames.append(user["username"])
    return f"Here is the list of attendees:\r\n {','.join([(f'<{username}>') for username in usernames])}"    

def bye_to_server(info: dict) -> str:
    return f"<{info['username']}> left the chat room.\n"
                    
def custom_print(message):
    # Bold
    if "<_b>" in message:
        message = message.replace("<_b>", "")
        message = ("\033[1m" + message + "\033[0m")
    
    # Italic
    if "<_i>" in message:
        message = message.replace("<_i>", "")
        message = ("\033[3m" + message + "\033[0m")
    
    # Underline
    if "<_u>" in message:
        message = message.replace("<_u>", "")
        message = ("\033[4m" + message + "\033[0m")
    
    # highlight
    if "<_h>" in message:
        message = message.replace("<_h>", "")
        message = ("\033[7m" + message + "\033[0m")

    message = _link(message)
    print(message)
    
# Highlighting links in the text
def _link(message):
    pattern = r'https?://\S+'
    urls = re.findall(pattern, message)
    for url in urls:
        message = message.replace(url, "\033[7m" + Styling.colors["link"] + url + "\033[0m")
