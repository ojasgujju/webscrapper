import argparse
import time
import random
from utils.download_utils import DownloadManager
import config

def read_urls(file_path):
    """Read URLs from a text file"""
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def main():
    parser = argparse.ArgumentParser(description="Batch file downloader with proxy rotation")
    parser.add_argument("url_file", help="Text file containing URLs to download")
    parser.add_argument("--no-proxy", action="store_true", help="Disable proxy usage")
    parser.add_argument("--min-delay", type=int, default=config.MIN_DELAY, 
                       help=f"Minimum delay between downloads (default: {config.MIN_DELAY}s)")
    parser.add_argument("--max-delay", type=int, default=config.MAX_DELAY, 
                       help=f"Maximum delay between downloads (default: {config.MAX_DELAY}s)")
    
    args = parser.parse_args()
    
    # Update configuration based on arguments
    config.USE_PROXY_SERVER = not args.no_proxy
    config.MIN_DELAY = args.min_delay
    config.MAX_DELAY = args.max_delay
    
    # Initialize downloader
    downloader = DownloadManager()
    
    # Read URLs
    urls = read_urls(args.url_file)
    total_urls = len(urls)
    successful_downloads = 0
    
    print(f"Found {total_urls} URLs to process")
    
    # Process each URL
    for i, url in enumerate(urls, 1):
        print(f"\nProcessing URL {i}/{total_urls}")
        print(f"URL: {url}")
        
        if downloader.download_file(url):
            successful_downloads += 1
            
        if i < total_urls:  # Don't delay after the last download
            delay = random.uniform(config.MIN_DELAY, config.MAX_DELAY)
            print(f"Waiting {delay:.1f} seconds before next download...")
            time.sleep(delay)
    
    # Print summary
    print("\nDownload Summary:")
    print(f"Total URLs processed: {total_urls}")
    print(f"Successfully downloaded: {successful_downloads}")
    print(f"Failed downloads: {total_urls - successful_downloads}")

if __name__ == "__main__":
    main()