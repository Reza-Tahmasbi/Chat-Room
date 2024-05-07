import os

class History:
    def __init__(self) -> None:
        """
        Initialize the History class and create a directory for storing chat history.

        This method creates a 'History' directory if it doesn't exist and opens a file 'history.txt' for appending messages.
        """
        os.makedirs("History", exist_ok=True)
        with open("History/history.txt", "a") as file:
            self.file = file
            file.close()
        
    def edit_history(self, message: str) -> None:
        """
        Append a message to the chat history file.

        Args:
            message (str): The message to be added to the chat history.

        This method opens the 'history.txt' file in append mode and writes the provided message to it.
        """
        file = open("History/history.txt", "a")
        file.write("\n" + message)