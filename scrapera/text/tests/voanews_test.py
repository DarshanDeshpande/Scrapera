from scrapera.text.voice_of_america import VOAScraper

scraper = VOAScraper()
scraper.scrape(num_pages=5, out_path='path/to/output/directory', sleep=2)
