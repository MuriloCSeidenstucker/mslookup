from ttkthemes import ThemedTk
from mslookup.interface.main_window import MainWindow

def start():
    root = ThemedTk(theme='itft1')
    app = MainWindow(root)
    app.run()

if __name__ == "__main__":
    start()