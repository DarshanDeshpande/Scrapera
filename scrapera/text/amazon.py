import os
import re
import sqlite3
from tqdm import tqdm
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class AmazonReviewScraper:
    '''
    Scraper for Amazon product reviews
    Args:
        driver_path: str, Path to chromedriver executable file
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
        chromedriver_proxy: [Optional] dict, A dictionary containing proxy information for the webdriver
    '''
    def __init__(self, driver_path, out_path=None, chromedriver_proxy=None):
        if out_path is not None and not os.path.isdir(out_path):
            raise NotADirectoryError("Invalid path to output directory")

        assert os.path.isfile(driver_path), "Invalid Chromedriver path received"

        self.conn = sqlite3.connect(
            os.path.join(out_path, 'AmazonProductReviews.db') if out_path else 'AmazonProductReviews.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS REVIEWS (ID INTEGER PRIMARY KEY AUTOINCREMENT,"
                       "REVIEW TEXT,"
                       "RATING NUMBER)")

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        if chromedriver_proxy is not None:
            webdriver.DesiredCapabilities.CHROME['proxy'] = chromedriver_proxy
        self.driver = webdriver.Chrome(driver_path, options=chrome_options)

    def _scrape_links(self, query, num_pages=1):
        all_links = set()
        for page in range(num_pages):
            link = f'https://www.amazon.com/s?k={query}&page={page + 1}'
            self.driver.get(link)
            a_tags = self.driver.find_elements_by_class_name('a-link-normal')
            for a_tag in a_tags:
                href = a_tag.get_attribute('href')
                flag = True if re.findall(r's[/]?\?k=', href) != [] else False
                if 'customerReviews' not in href and not flag \
                        and 'help' not in href and 'amazon-adsystem' not in href:
                    all_links.add(href)
        return all_links

    def _scrape_products(self, all_links, num_reviews=10, sleep=5):
        for link in tqdm(all_links):
            try:
                self.driver.get(link)
                # description = driver.find_element_by_id("productDescription").find_element_by_tag_name('p').text
                time.sleep(1)
                self.driver.find_element_by_partial_link_text('See all reviews').click()
                for _ in range(num_reviews // 10):
                    for i in range(10):
                        review = self.driver.execute_script(
                            f"return document.getElementsByClassName('review-text-content')[{i}].innerText")
                        rating = self.driver.execute_script(
                            f'''return document.querySelectorAll("[data-hook='review-star-rating']")[{i}].innerText''')
                        if review != '' and review is not None:
                            self.cursor.execute("INSERT INTO REVIEWS VALUES (?,?,?)", (None, review, float(rating.split(' ')[0])))
                        else:
                            break
                    self.driver.execute_script(f'''document.getElementsByClassName('a-last')[0].firstElementChild.click()''')
                    self.conn.commit()
                    print(f"Sleeping for {sleep} seconds to avoid excessive requests or blocking")
                    time.sleep(sleep)
            except Exception:
                self.conn.commit()
                print("Invalid link encountered. Skipping")
                continue
        print(f"Extraction finished")

    def scrape(self, query, num_pages=1, num_reviews=10, sleep=5):
        '''
        Scrapes product reviews for a specific query and writes the results in a SQLite database
        query: str, Keywords used for fetching
        num_pages: int, Number of pages to be fetched. Default is 1
        num_reviews: int, Number of reviews per product. Default is 10
        sleep: float, Amount of time to sleep between successive fetches. Sleeping reduces chances of HTTP Error 429 (Excessive Requests)
        '''
        query = str(query).replace(' ', '+')
        assert num_pages >= 1, f"Number of pages must be greater than 0. Receiver {num_pages}"
        assert num_reviews >= 1
        assert sleep >= 0, "Sleep time cannot be negative"
        if num_reviews % 10 != 0:
            print(f"WARNING: Number of reviews will be the closest multiple of 10 to {num_reviews}"
                  " because of fetching restrictions")
        all_links = self._scrape_links(query, num_pages)
        self._scrape_products(all_links, num_reviews, sleep)
        self.conn.close()
        self.driver.close()
