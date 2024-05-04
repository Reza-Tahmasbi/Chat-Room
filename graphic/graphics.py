# import PySimpleGUI as sg

# def steam_login_form():
#     sg.theme('DarkBlue')
#     # Define the layout
#     layout = [
#         [sg.Text('Click the text to open a link', enable_events=True, key='-LINK-', font=('Helvetica', 14, 'underline'))],
#         [sg.Text('', key='-OUTPUT-', font=('Helvetica', 14))],
#         [sg.Text('Welcome to ur lovely chatroom', font=('Arial', 20), pad=5, text_color="White")],
#         [sg.Text('Sign in', font=('Arial', 20), pad=22)],
#         [sg.Text('Username', size=(10, 2), font=('Arial', 14)), sg.InputText(size=(25, 1), font=('Arial', 14), key='-USERNAME-')],
#         [sg.Text('Password', size=(10, 2), font=('Arial', 14)), sg.InputText(size=(25, 1), font=('Arial', 14), password_char='*', key='-PASSWORD-')],
#         [sg.Checkbox('Remember me', font=('Arial', 12), key='-REMEMBER-')],
#         [sg.Button('Sign in', size=(10, 1), font=('Arial', 14), key='-SIGNIN-'), sg.Button('Cancel', size=(10, 1), font=('Arial', 14), key='-CANCEL-')]
#     ]

#     # Create the window
#     window = sg.Window('Steam Login', layout, size=(500, 400), element_justification='center')

#     while True:
#         event, values = window.read()
#         if event == sg.WIN_CLOSED or event == '-CANCEL-':
#             break
#         elif event == '-SIGNIN-':
#             username = values['-USERNAME-']
#             password = values['-PASSWORD-']
#             remember = values['-REMEMBER-']
#             # Perform login logic here
#             print(f"Attempting to log in with username: {username}, password: {password}, remember: {remember}")
#             # Clear the form fields
#             window['-USERNAME-'].update('')
#             window['-PASSWORD-'].update('')
#             window['-REMEMBER-'].update(False)

#     window.close()

# if __name__ == "__main__":
#     steam_login_form()
    
    
import PySimpleGUI as sg
import webbrowser

def open_new_window():
    layout = [[sg.Text("This is a new window")], [sg.Button("Close")]]
    new_window = sg.Window("New Window", layout, modal=True)
    
    while True:
        event, values = new_window.read()
        if event == sg.WINDOW_CLOSED or event == "Close":
            new_window.close()
            break

layout = [
    [sg.Text('Click the text to open a new window', enable_events=True, key='-LINK-', font=('Helvetica', 14, 'underline'))],
]

window = sg.Window('Clickable Text', layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    elif event == '-LINK-':
        open_new_window()

