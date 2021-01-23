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
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

Scrapera provides access to a variety of scraper scripts for most commonly used machine learning and data science domains, mainly consisting of scrapers for 
<li>Images</li>
<li>Text</li>
<li>Audio</li>
<li>Videos</li>
<br>
This main aim of this package is to cluster common scraping tasks so as to make it more convenient for ML researchers and engineers to focus on their models rather than worrying about the data collection process 
<br><br/>

>DISCLAIMER: Owner or Contributors do not take any responsibility for misuse of data obtained through Scrapera. Contact the owner if copyright terms are violated due to any module provided by Scrapera.  

## Prerequisites

All prerequisites can be installed separately through the `requirements.txt` file as below

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
from Scrapera.Video import VimeoScraper
scraper = VimeoScraper(out_path='path/to/output/directory')
scraper.scrape(url='https://vimeo.com/191955190', quality='720p')
```

_For more examples, please refer to the individual test folders in respective modules_



<!-- ROADMAP -->
## Roadmap

<summary>Known issues</summary>
<ul>
    Instagram Comments Scraper needs updation due to GraphQL changes
</ul>


<!-- CONTRIBUTING -->
## Contributing

Scrapera welcomes any and all contributions and scraper requests. Feel free to fork the repository and add your own scrapers to help the community!


<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.


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
[version-shield]: https://img.shields.io/badge/VERSION-1.0.0-orange?style=for-the-badge
[python-shield]: https://img.shields.io/badge/PYTHON-3.6%7C3.7%7C3.8-blue?style=for-the-badge