from scrapera.miscellaneous.yahoo_stocks import YahooScraper

scraper = YahooScraper()
scraper.scrape(ticker='AMZN', interval='1d', range_of_data='1mo', out_path=r'path/to/output/directory')
