import os
import sys
from queue import Queue
from tkinter import Tk, ttk, Frame, Text
from tkinter import LEFT, TOP, BOTTOM, BOTH, END

# I hate python imports. Fix for run via cmd inside venv
current_file = os.path.realpath(__file__)
current_dir = os.path.dirname(current_file)
repo_dir = os.path.abspath(os.path.join(current_dir, '..', '..'))
sys.path.insert(0, repo_dir)

from client_side.gui import settings
from client_side.backend.listener import run_listener
from client_side.backend.sender import ClientSender

# Lasy way to get username and password
if len(sys.argv) == 4:
    MY_USERNAME = sys.argv[1]
    MY_PASSWORD = sys.argv[2]
    MY_COMPANION = sys.argv[3]

else:
    MY_USERNAME = 'user_1'
    MY_PASSWORD = 'qwerty'
    MY_COMPANION = 'user_2'


main_window = Tk()
side_menu = Frame(main_window, bg='grey')
conversation_widget = Text(master=main_window, height=10)
type_widget = Text(master=main_window, height=10)

sender = ClientSender()
queue = Queue()
run_listener(queue)


response = sender.login_request({'username': MY_USERNAME, 'password': MY_PASSWORD})
if response and response.status_code == 200:
    MY_SESSION_ID = response.json().get('session_id')
    MY_USER_ID = response.json().get('user_id')
else:
    quit('Cannot login.')

response = sender.user_request({'username': MY_COMPANION, 'session_id': MY_SESSION_ID, 'request': 'get_user'})
if response and response.status_code == 200:
    COMPANION_USER_ID = response.json().get('user_id')
else:
    quit('Cannot get user id.')


def check_received_messages():
    # If queue has message, check again after 0.1 sec
    if not queue.empty():
        json_dict = queue.get()
        conversation_widget.after(100, check_received_messages)

        if 'message' in json_dict.keys():
            put_message(json_dict)

    # or check again after 1 sec
    else:
        conversation_widget.after(1000, check_received_messages)


def send_message():
    text = type_widget.get('1.0', END).strip()
    type_widget.delete('1.0', END)

    if text:
        json_dict = {'message': text, 'sender_id': MY_USER_ID, 'sender_username': MY_USERNAME,
                     'receiver_id': COMPANION_USER_ID, 'session_id': MY_SESSION_ID}

        response = sender.message_request(json_dict)
        if response and response.status_code == 200:
            put_message({'username': MY_USERNAME, 'message': text})


def put_message(json_dict):
    username = json_dict.get('username') if json_dict.get('username') else json_dict.get('sender_username')
    message = json_dict.get('message')
    string = f'{username}: {message}\n'
    conversation_widget.insert(index=END, chars=string)


if __name__ == "__main__":

    # Main window
    main_window.title(f'{settings.WINDOW_TITLE}: {MY_USERNAME}')
    main_window.geometry(f'{settings.WINDOW_RESOLUTION}+{settings.WINDOW_POSITION_SHIFT}')
    main_window.configure(bg=settings.WINDOW_BACKGROUND)

    # Side menu
    side_menu.pack_propagate(True)
    side_menu.pack(fill=BOTH, side=LEFT)

    # Quit button
    button_quit = ttk.Button(side_menu, text='Quit', command=main_window.destroy)
    button_quit.pack(padx=5, pady=10)

    # Conversation text field
    conversation_widget.pack(side=TOP, fill=BOTH, expand=True)
    conversation_widget.after(1000, check_received_messages)

    # Send button
    button_quit = ttk.Button(main_window, text='Send', command=send_message)
    button_quit.pack(side=BOTTOM, padx=5, pady=10)

    # Type text field
    type_widget.pack(side=BOTTOM, fill=BOTH, expand=True)

    main_window.mainloop()
