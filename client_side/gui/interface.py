from client_side.gui import settings
from queue import Queue
from tkinter import Tk, ttk, Frame, Text
from tkinter import LEFT, TOP, BOTTOM, BOTH

from client_side.backend.listener import run_listener
from client_side.backend.sender import ClientSender

main_window = Tk()
side_menu = Frame(main_window, bg='grey')
conversation_widget = Text(master=main_window, height=10, bg='blue')
type_widget = Text(master=main_window, height=10, bg='green')

sender = ClientSender()


if __name__ == "__main__":
    # Start http listener
    queue = Queue()
    run_listener(queue)

    # Main window
    main_window.title(settings.WINDOW_TITLE)
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

    # Send button
    button_quit = ttk.Button(main_window, text='Send')
    button_quit.pack(side=BOTTOM, padx=5, pady=10)

    # Type text field
    type_widget.pack(side=BOTTOM, fill=BOTH, expand=True)

    main_window.mainloop()
