import os
import logging

dir_path = os.path.dirname(os.path.realpath(__file__))
filename = os.path.join(dir_path, 'app.log')

# Initialize the logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(filename)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)

if __name__ == '__main__':
    logger.info("App logger test")

