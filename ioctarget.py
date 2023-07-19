import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback
from cache import IOC_Cache
from source import ioc_selectors
from iocscrape import IOCScraper
import random
from fake_useragent import UserAgent
import time

logging.basicConfig(filename='error.log', level=logging.ERROR)


class IOCTarget:
    def __init__(self, target_url):
        self.target_url = target_url
        self.session = requests.Session()
        self.session.headers = {'User-Agent': UserAgent().random}

    def handle_error(self, func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_message = f"Error occurred in function {func.__name__}: {e}\n"
                error_message += traceback.format_exc()
                logging.error(error_message)
                print(f"Error occurred in function {func.__name__}: {e}")

        return wrapper

    def scrape_iocs(self, url):
        response = self.session.get(url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        iocs = []
        for ioc_selector in ioc_selectors:
            iocs.extend([ioc_element.get_text().strip() for ioc_element in soup.select(ioc_selector)])

        return iocs

    def scrape_with_pagination(self):
        page = 1
        all_iocs = []

        while True:
            paginated_url = f"{self.target_url}?page={page}"
            iocs = self.scrape_iocs(paginated_url)

            if not iocs:
                break

            all_iocs.extend(iocs)
            page += 1
            time.sleep(0.5)  # Add a smaller delay between each page request for improved performance

        return all_iocs

    def scrape_in_parallel(self):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.scrape_with_pagination)]

            all_iocs = []
            for future in as_completed(futures):
                iocs = future.result()
                all_iocs.extend(iocs)
                time.sleep(0.5)  # Add a smaller delay between each parallel scrape for improved performance

        return all_iocs


if __name__ == '__main__':
    target_url = input("Enter the target URL: ")
    
    ioctarget = IOCTarget(target_url)
    iocs = ioctarget.scrape_in_parallel()

    print("IOCs found on the target:")
    print(iocs)
