# modules/logger.py
import logging
from logging.handlers import RotatingFileHandler
from config import LOG_CONFIG

def setup_logger(name, log_file, level=logging.INFO):
    """Configure and return a logger instance"""
    # Create formatter
    formatter = logging.Formatter(
        fmt=LOG_CONFIG['format'],
        datefmt=LOG_CONFIG['date_format']
    )

    # Create handlers
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=100*1024*1024,  # 100MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.FileHandler(log_file)
    console_handler.setFormatter(formatter)

    # Create and configure logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Add handlers
    logger.addHandler(file_handler)
    # logger.addHandler(console_handler)

    return logger

# Create loggers
ha_logger = setup_logger('home_assistant', LOG_CONFIG['home_assistant'])
openai_logger = setup_logger('openai', LOG_CONFIG['openai'])
db_logger = setup_logger('database', LOG_CONFIG['database'])

app_logger = setup_logger('app', LOG_CONFIG['app'])
