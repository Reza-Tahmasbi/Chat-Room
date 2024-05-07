import os

class History:
    def __init__(self) -> None:
        os.makedirs("History", exist_ok = True)
        with open("History/history.txt", "a") as file:
            self.file = file
            file.close()
        
    def edit_history(self, message: str) -> None:
        file =  open("History/history.txt", "a")
        file.write("\n" + message)
            