from scrapera.text.imdb import IMDBReviewsScraper

scraper = IMDBReviewsScraper()
scraper.scrape('how i met your mother', num_scrolls=1, sleep=10)
