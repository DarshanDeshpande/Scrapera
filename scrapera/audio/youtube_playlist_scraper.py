# !python -m pip install git+https://github.com/nficano/pytube
import glob
import os
import re
import shutil
import subprocess

from pytube import Playlist as _Playlist
from pytube import YouTube as _YouTube
from tqdm import tqdm


class PlaylistScraper:
    '''
    Class for Youtube Playlist Scraper
    Args:
        url : str, URL to the Youtube playlist
        bitrate: int, Bitrate of output audio files. Output files will have a constant bitrate (CBR) of 'bitrate' kbps
        out_path: [Optional] Path to the output directory. If unspecified, current directory is used
    '''
    def __init__(self, url, bitrate, out_path):
        assert type(bitrate) == int and bitrate in [16, 24, 32, 48, 56, 64, 96, 128, 160, 192, 256, 320],\
            "Bitrate must be one of [16,24,32,48,56,64,96,128,160,192,256,320]"

        self.url = url
        self.bitrate = bitrate
        self.out_path = out_path if os.path.isdir(out_path) else 'AudioFiles'

    def download(self, num_songs, proxies=None):
        '''
        num_songs: int, Number of songs to extract from the playlist
        proxies: dict, A dictionary containing http or https proxies
        '''
        # Creating throwaway directory
        os.mkdir('Scraped')

        path = r'Scraped'
        playlist = _Playlist(self.url, proxies=proxies)

        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        print(f"{len(playlist.video_urls)} videos found")

        num_songs = len(playlist.video_urls) if num_songs < 0 else num_songs

        for url in tqdm(sorted(playlist.video_urls)[:num_songs]):
            yt = _YouTube(url, proxies)
            audio = yt.streams.get_audio_only()
            audio.download(path)
            name = yt.title
            mp4 = '"Scraped/%s.mp4" -codec:a libmp3lame -b:a %sK -vn ' % (name, self.bitrate)
            mp3 = '"%s/%s.mp3"' % (self.out_path, name)
            ffmpeg = ('''ffmpeg -i %s''' % mp4 + mp3)
            subprocess.call(ffmpeg, shell=True)

        shutil.rmtree('Scraped')
        print(f'Download Completed. Downloaded {len(glob.glob(f"{self.out_path}/*"))} songs')
