import os
import time
import random
from urllib.parse import urlparse, unquote
import requests
from requests.auth import HTTPProxyAuth

from utils.proxy_utils.proxy import Proxy
from utils.user_agent_utils.user_agent import UserAgent
import config

class DownloadManager:
    def __init__(self):
        self.proxy_manager = Proxy()
        self.user_agents = UserAgent()
        
        # Create download directory if it doesn't exist
        if not os.path.exists(config.DOWNLOAD_DIR):
            os.makedirs(config.DOWNLOAD_DIR)
    
    def get_filename_from_url(self, url):
        """Extract and clean filename from URL"""
        parsed_url = urlparse(url)
        filename = unquote(os.path.basename(parsed_url.path))
        
        # If no filename in URL, create one from the URL
        if not filename:
            filename = f"file_{hash(url)}.pdf"
        
        # Clean filename of invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
            
        return filename
    
    def download_file(self, url, custom_filename=None):
        """Download a single file with proxy rotation and retry logic"""
        filename = custom_filename or self.get_filename_from_url(url)
        filepath = os.path.join(config.DOWNLOAD_DIR, filename)
        
        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"File already exists: {filename}")
            return True
            
        headers = {'User-Agent': self.user_agents.user_agent()}
        retries = 0
        
        while retries < config.MAX_RETRIES:
            try:
                if config.USE_PROXY_SERVER:
                    proxy = self.proxy_manager.generate_proxy()
                    auth = HTTPProxyAuth("", "")
                    response = requests.get(
                        url,
                        proxies=proxy,
                        auth=auth,
                        headers=headers,
                        timeout=config.TIMEOUT,
                        stream=True,
                        verify=True
                    )
                else:
                    response = requests.get(
                        url,
                        headers=headers,
                        timeout=config.TIMEOUT,
                        stream=True,
                        verify=True
                    )

                if response.status_code == 200:
                    # Check file size if limit is set
                    size = int(response.headers.get('content-length', 0))
                    if config.MAX_FILE_SIZE and size > config.MAX_FILE_SIZE * 1024 * 1024:
                        print(f"File too large: {size/(1024*1024):.1f} MB (limit: {config.MAX_FILE_SIZE} MB)")
                        return False

                    # Download with progress bar
                    print(f"\nDownloading: {filename}")
                    with open(filepath, 'wb') as f:
                        downloaded = 0
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if size:
                                    progress = (downloaded / size) * 100
                                    print(f"\rProgress: {progress:.1f}%", end="")
                    
                    print(f"\nSuccessfully downloaded: {filename}")
                    return True
                
                else:
                    print(f"HTTP Error {response.status_code} for {url}")
                    retries += 1
                    
            except Exception as e:
                print(f"Error downloading {url}: {str(e)}")
                if config.USE_PROXY_SERVER:
                    # Remove failed proxy
                    self.proxy_manager.proxy_list.remove(proxy.get("http"))
                    self.proxy_manager.write_proxy_list()
                retries += 1
                
            if retries < config.MAX_RETRIES:
                delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
                print(f"Retrying in {delay:.1f} seconds... (Attempt {retries + 1}/{config.MAX_RETRIES})")
                time.sleep(delay)
                
        print(f"Failed to download {url} after {config.MAX_RETRIES} attempts")
        return False