import logging
from ttkthemes import ThemedTk
from mslookup.app.logger_config import configure_logging
from mslookup.interface.main_window import MainWindow

configure_logging()

def start():
    logging.info("Starting the application.")
    try:
        root = ThemedTk(theme='itft1')
        app = MainWindow(root)
        app.run()
    except Exception as e:
        logging.error("An error occurred while running the application", exc_info=True)
    finally:
        logging.info("Shutting down the application.\n")

if __name__ == "__main__":
    start()