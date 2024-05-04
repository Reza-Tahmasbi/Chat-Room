import PySimpleGUI as sg

def chat_room():
    # Define the layout
    layout = [
        [sg.Multiline(size=(80, 20), key='-CHAT-', autoscroll=True, disabled=True)],
        [sg.InputText(size=(60, 1), key='-MSG-'), sg.Button('Send', bind_return_key=True)],
        [sg.Button('Join'), sg.Button('Leave'), sg.Button('Clear')]
    ]

    # Create the window
    window = sg.Window('Chatroom', layout)

    # Chat history
    chat_history = []

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break

        # Handle user actions
        if event == 'Send':
            message = values['-MSG-'].strip()
            if message:
                chat_history.append(f"You: {message}")
                window['-CHAT-'].update('\n'.join(chat_history))
                window['-MSG-'].update('')

        elif event == 'Join':
            username = values['-MSG-'].strip()
            if username:
                chat_history.append(f"{username} has joined the chat.")
                window['-CHAT-'].update('\n'.join(chat_history))
                window['-MSG-'].update('')

        elif event == 'Leave':
            username = values['-MSG-'].strip()
            if username:
                chat_history.append(f"{username} has left the chat.")
                window['-CHAT-'].update('\n'.join(chat_history))
                window['-MSG-'].update('')

        elif event == 'Clear':
            chat_history.clear()
            window['-CHAT-'].update('')

    window.close()

if __name__ == "__main__":
    chat_room()
