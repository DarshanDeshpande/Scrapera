from scrapera.audio.youtube_playlist_scraper import PlaylistScraper

scraper = PlaylistScraper('https://youtube.com/playlist?list=PLGRMJyXiCaQsaubS3MldnaSIDW1chhdid', 320, '')
scraper.download(2)
