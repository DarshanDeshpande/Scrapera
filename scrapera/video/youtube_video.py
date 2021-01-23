import pytube
import os


class VideoScraper:
    '''
    Scraper class for a specified Youtube video
    Args:
        out_path:  [Optional] str, Path to output directory. If unspecified, current directory will be used
    '''
    def __init__(self, out_path=''):
        if out_path != '':
            assert os.path.isdir(out_path), "Invalid output directory"
        self.out_path = out_path

    def download(self, url, resolution=None, proxies=None):
        '''
        Scraper function for Youtube video scraping
        Args:
            url: URL of vimeo video to be scraped
            resolution: utput video resolution. If unspecified then highest quality available is chosen
            proxies: dict, A dictionary containing proxy information
        '''
        yt = pytube.YouTube(url, proxies=proxies)

        print("-"*75)
        print("File Details: ")
        print("Title: ", yt.title, "\nAuthor: ", yt.author, "\nLength: ", yt.length)
        print("-" * 75)

        if resolution:
            try:
                yt.streams.get_by_resolution(resolution).download(self.out_path)
            except Exception:
                raise ValueError(f"{resolution} resolution not available for this video. Select a valid resolution")
        else:
            yt.streams.get_highest_resolution().download(self.out_path)
