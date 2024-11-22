from ttkthemes import ThemedTk
from mslookup.app.logger_config import get_logger
from mslookup.interface.main_window import MainWindow

logger = get_logger(__name__)

def start():
    logger.info("Starting the application.")
    try:
        root = ThemedTk(theme='itft1')
        app = MainWindow(root)
        app.run()
    except Exception as e:
        logger.exception("An error occurred while running the application")
    finally:
        logger.info("Shutting down the application.\n")

if __name__ == "__main__":
    start()