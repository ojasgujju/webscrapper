import os

# Project directory paths
HOME_DIR = os.path.dirname(os.path.realpath(__file__))
DOWNLOAD_DIR = os.path.join(HOME_DIR, "downloads")

# Download settings
USE_PROXY_SERVER = True
MAX_RETRIES = 3
TIMEOUT = 30

# Delay settings (in seconds)
MIN_DELAY = 5
MAX_DELAY = 15

# File size limits (in MB)
MAX_FILE_SIZE = 500  # Set to None for no limit