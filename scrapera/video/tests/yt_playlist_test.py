from scrapera.video.youtube_playlist import PlaylistScraper

scraper = PlaylistScraper()
scraper.download('https://youtube.com/playlist?list=PLGRMJyXiCaQsaubS3MldnaSIDW1chhdid',
                 5, '360p')
