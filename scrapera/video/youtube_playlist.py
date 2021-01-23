import pytube
import os


class PlaylistScraper:
    '''
    Scraper for Youtube playlist scraping
    Args:
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
    '''
    def __init__(self, out_path=''):
        if out_path != '':
            assert os.path.isdir(out_path), "Invalid output directory"
        self.out_path = out_path

    def download(self, playlist_url, num_urls=-1, resolution=None, proxies=None):
        '''
        Scraper function for downloading videos from a youtube playlist
        Args:
            playlist_url: URL of vimeo video to be scraped
            num_urls: Maximum number of URLs to be fetched from the playlist
            resolution: Output video resolution. If unspecified then highest quality available is chosen
            proxies: dict, A dictionary containing proxy information
        '''
        if proxies is None:
            print("WARNING: No proxies received. "
                  "All videos might not get downloaded because of HTTP Error 429 (Too Many Requests)")
        playlist = pytube.Playlist(playlist_url, proxies)
        video_urls = playlist.video_urls
        for url in video_urls[:num_urls]:
            yt = pytube.YouTube(url)

            print("-"*75)
            print("File Details: ")
            print("Title: ", yt.title, "\nAuthor: ", yt.author, "\nLength: ", yt.length)
            print("-" * 75)

            if resolution:
                yt.streams.get_by_resolution(resolution).download(self.out_path)
            else:
                yt.streams.get_highest_resolution().download(self.out_path)

            print(f"Finished downloading {yt.title}")
