from scrapera.text.voice_of_america import VOAScraper

scraper = VOAScraper()
scraper.scrape(num_pages=3, out_path='path/to/output/directory', proxies=['http://46.4.96.137:8080',
                                                                          'http://176.9.75.42:8080',
                                                                          'http://154.16.202.22:8080'])
