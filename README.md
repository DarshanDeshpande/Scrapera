<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="">
    <img src="https://i.imgur.com/ig6vLCJ.png" alt="Logo"  width="80%" height="70%">
  </a>
</p>


<!-- PROJECT SHIELDS -->
[![MIT License][license-shield]][license-url]
![version-shield]
![release-shield]
![python-shield]



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#sponsors">Sponsors</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Scrapera is a completely **Chromedriver free** package that provides access to a variety of scraper scripts for most commonly used machine learning and data science domains. Scrapera directly and asynchronously scrapes from public API endpoints, thereby removing the heavy browser overhead which makes Scrapera extremely fast and robust to DOM changes. Currently, Scrapera supports the following crawlers: 
<li>Images
    <ul>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/image/duckduckgo.py">DuckDuckGo Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/image/giphy.py">GIPHY Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/image/tumblr.py">Tumblr Scraper</a> (Deprecated)</li>
    </ul>
</li>
<li>Text
    <ul>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/amazon.py">Amazon Product Reviews</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/walmart.py">Walmart Product Reviews</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/voice_of_america.py">Voice of America News Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/scroll_news.py">Scroll News Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/imdb.py">IMDB Reviews Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/reddit.py">Reddit Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/text/medium.py">Medium Scraper</a></li>
    </ul>
</li>
<li>Audio
    <ul>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/audio/youtube_playlist_scraper.py">Youtube Playlist Scraper</a></li>
    </ul>
</li>
<li>Videos
    <ul>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/video/vimeo.py">Vimeo Scraper</a></li>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/video/youtube.py">Youtube Scraper</a></li>
    </ul>
</li>

<li>Miscellaneous
    <ul>
        <li><a href="https://github.com/DarshanDeshpande/Scrapera/blob/master/scrapera/miscellaneous/yahoo_stocks.py">Yahoo Stocks Scraper</a></li>
    </ul>
</li>
<br>
The main aim of this package is to cluster common scraping tasks so as to make it more convenient for ML researchers and engineers to focus on their models rather than worrying about the data collection process 
<br><br/>

>DISCLAIMER: Owner or Contributors do not take any responsibility for misuse of data obtained through Scrapera. Contact the owner if copyright terms are violated due to any module provided by Scrapera.  

## Prerequisites

Prerequisites can be installed separately through the `requirements.txt` file as below

```sh
pip install -r requirements.txt
```


 
## Installation

Scrapera is built with Python 3 and can be `pip` installed directly

```sh
pip install scrapera
```


Alternatively, if you wish to install the latest version directly through GitHub then run
```sh
pip install git+https://github.com/DarshanDeshpande/Scrapera.git
```


<!-- USAGE EXAMPLES -->
## Usage

To use any sub-module, you just need to import, instantiate and execute
```python
from scrapera.video.vimeo import VimeoScraper
scraper = VimeoScraper()
scraper.scrape('https://vimeo.com/191955190', '540p')
```

_For more examples, please refer to the individual test folders in respective modules_


<!-- CONTRIBUTING -->
## Contributing

Scrapera welcomes any and all contributions and scraper requests. Please raise an issue if the scraper fails at any instance. Feel free to fork the repository and add your own scrapers to help the community!
<br>
For more guidelines, refer to `CONTRIBUTING`

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

## Sponsors

<a href="https://serpapi.com/">
    <img src="https://i.imgur.com/CBOSxrm.png" alt="Logo"  width="165px" height="65px">
  </a>

<!-- CONTACT -->
## Contact
Feel free to reach out for any issues or requests related to Scrapera

Darshan Deshpande (Owner) - [Email](https://mail.google.com/mail/u/0/?view=cm&fs=1&to=darshan1504@gmail.com&tf=1) | [LinkedIn](https://www.linkedin.com/in/darshan-deshpande/)



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements
* <a href="https://github.com/pytube/pytube"> PyTube </a>





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/badge/CONTRIBUTORS-1-orange?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[license-shield]: https://img.shields.io/badge/LICENSE-MIT-brightgreen?style=for-the-badge
[license-url]: https://github.com/DarshanDeshpande/Scrapera/blob/master/LICENSE.txt
[version-shield]: https://img.shields.io/badge/VERSION-1.1.3-orange?style=for-the-badge
[python-shield]: https://img.shields.io/badge/PYTHON-3.6%7C3.7%7C3.8-blue?style=for-the-badge
[release-shield]: https://img.shields.io/badge/Build-Stable-yellow?style=for-the-badge
