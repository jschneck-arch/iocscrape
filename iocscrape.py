import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import traceback
from cache import IOC_Cache
from source import sources
import random
from fake_useragent import UserAgent
import time
from datetime import datetime 

logging.basicConfig(filename='error.log', level=logging.ERROR)


class IOCScraper:
    def __init__(self, source):
        self.source = source
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

        iocs = [ioc_element.get_text().strip() for ioc_element in soup.select(self.source['ioc_selector'])]

        return iocs

    def scrape_with_pagination(self):
        page = 1
        all_iocs = []

        while True:
            paginated_url = f"{self.source['url']}?page={page}"
            iocs = self.scrape_iocs(paginated_url)

            if not iocs or not self.is_latest(iocs):
                break

            all_iocs.extend(iocs)
            page += 1
            time.sleep(0.5)  # Add a smaller delay between each page request for improved performance

        return all_iocs

    def is_latest(self, iocs):
        cutoff_date = datetime.now()

        for ioc in iocs:
            ioc_date = self.extract_date(ioc['date'])

            if ioc_date is None:
                continue

            if ioc_date > cutoff_date:
                return False

        return True


    def extract_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            return None

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
    cache = IOC_Cache()  # Initialize the cache object

    all_iocs = []

    for source in sources:
        scraper = IOCScraper(source)

        if cache.is_cached(source['url']):  # Check if IOCs are cached
            iocs = cache.get_cached_iocs(source['url'])
        else:
            iocs = scraper.scrape_in_parallel()
            cache.cache_iocs(source['url'], iocs)  # Cache the scraped IOCs

        all_iocs.extend(iocs)

    print("All IOCs:")
    print(all_iocs)
