from scrapera.video.youtube import PlaylistScraper, VideoScraper

scraper = PlaylistScraper()
scraper.download('https://youtube.com/playlist?list=PLGRMJyXiCaQsaubS3MldnaSIDW1chhdid',
                 5, '360p')

scraper = VideoScraper()
scraper.download('https://youtu.be/i6ktmYF3lhE', '360p')
