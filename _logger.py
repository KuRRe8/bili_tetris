import logging
import os
from datetime import datetime
import config.settings

# Define a global logger
def setup_logger(log_file="app.log", level=logging.INFO):
    """Setup and return a logger instance."""
    logger = logging.getLogger()
    logger.setLevel(level)

    # Create file handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Define formatter and add it to handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info('###Logger initialized.###')
    return logger


# Initialize the global logger
current_date = datetime.now().strftime("%Y-%m-%d")
LOG_FILE_PATH = os.path.join(os.path.dirname(__file__), "logs", f"app.{datetime.now().strftime('%Y-%m-%d_%H-%M')}.log")
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)
logger = setup_logger(log_file=LOG_FILE_PATH,level=config.settings.LOGGER_LVL)

# Example usage
if __name__ == "__main__":
    logger.debug('Test the debug level log.')
    logger.info('Test the info level log.')
    logger.warning('Test the warning level log.')
    logger.error('Test the error level log.')
    logger.critical('Test the critical level log.')
    