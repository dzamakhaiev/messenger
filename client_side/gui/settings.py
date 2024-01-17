import tkinter as tk

# Get screen resolution
root = tk.Tk()
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.destroy()
root.quit()

# WINDOW CONFIG
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_RESOLUTION = f'{WINDOW_WIDTH}x{WINDOW_HEIGHT}'
WINDOW_POSITION_SHIFT = f'{(screen_width//2)-(WINDOW_WIDTH//2)}+{(screen_height//2)-(WINDOW_HEIGHT//2)}'
WINDOW_TITLE = 'Messenger'
WINDOW_BACKGROUND = 'white'

# BUTTONS CONFIG
BUTTON_WIDTH = 50
BUTTON_PADDING = 5
