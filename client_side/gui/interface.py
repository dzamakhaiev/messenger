import settings
from tkinter import Tk, ttk, Frame, Text
from tkinter import CENTER, NO

main_window = Tk()
channel_menu = Frame(main_window, bg='grey')
channel_table = ttk.Treeview(master=main_window)
log_widget = Text(master=main_window, height=10, bg='green')


if __name__ == "__main__":

    # Main window
    main_window.title(settings.WINDOW_TITLE)
    main_window.geometry(f'{settings.WINDOW_RESOLUTION}+{settings.WINDOW_POSITION_SHIFT}')
    main_window.configure(bg=settings.WINDOW_BACKGROUND)

    # Create channel's menu
    channel_menu.pack_propagate(True)
    channel_menu.pack(fill='both', side='left')

    # Add quit button
    button_quit = ttk.Button(channel_menu, text='Quit', command=main_window.destroy)
    button_quit.pack(padx=5, pady=10)

    # Add text widget for logs
    log_widget.pack(side='bottom', fill='x', expand=True)

    main_window.mainloop()
