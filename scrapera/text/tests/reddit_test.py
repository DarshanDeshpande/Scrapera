from scrapera.text.reddit import RedditPostScraper

scraper= RedditPostScraper()
scraper.scrape(topic="python", numposts=20)