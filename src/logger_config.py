import logging
import os


def setup_logger(
    name: str, log_file: str, level: int = logging.INFO
) -> logging.Logger:
    """Configura e retorna um logger com o nome e arquivo de log especificados."""
    log_dir = 'logs'
    os.makedirs(log_dir, exist_ok=True)

    log_path = os.path.join(log_dir, log_file)

    handler = logging.FileHandler(log_path, mode='w')
    handler.setLevel(level)
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


main_logger = setup_logger('main_logger', 'project.log')
