from colorama import Fore

colors = {
    "Warning": Fore.YELLOW,
    "Success": Fore.GREEN,
    "System": Fore.CYAN,
    "link": Fore.MAGENTA
}

# Bold
def _b(message: str) -> str:
    return ("\033[1m" + message + "\033[0m")

# Italic
def _i(message: str) -> str:
    return ("\033[3m" + message + "\033[0m")

# Underline
def _u(message: str) -> str:
    return ("\033[4m" + message + "\033[0m")

# highlight
def _h(message: str) -> str:
    return ("\033[7m" + message + "\033[0m")

# Link 
def _link(message: str) -> str:
    return _u(_b(_h((colors["link"] + message))))