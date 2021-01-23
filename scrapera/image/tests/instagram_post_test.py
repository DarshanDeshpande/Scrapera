from scrapera.image.instagram import InstagramImageScraper

scraper = InstagramImageScraper()
scraper.scrape('https://www.instagram.com/p/CKKENR5pIxx/', resize=(500, 500))
