import logging
import os

def setup_logger(log_file="../loggin/logs/app.log", level=logging.DEBUG):
    # Ensure the directory for the log file exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file), 
            logging.StreamHandler()
        ]
    )
