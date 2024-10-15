import tkinter as tk
from mslookup.interface.main_window import MainWindow

def start():
    root = tk.Tk()
    app = MainWindow(root)
    app.run()

if __name__ == "__main__":
    start()