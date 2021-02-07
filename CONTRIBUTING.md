# Introduction

### Contributing to Scrapera

Thank you for considering contributing to Scrapera. It's people like you that make Scrapera a success. The source is always available on GitHub and will be open to all contributions, whether it be bug fixes or scraper additions.

### Why read the guidelines?

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open source project. In return, they should reciprocate that respect in addressing your issue, assessing changes, and helping you finalize your pull requests.

### How can you Contribute? 

You can contribute to this project by 
<li> Improving documentation</li>
<li> Bug reporting and corrections </li>
<li> Creating tests for new or updated modules </li>
<li> Adding custom scrapers</li>
<li> Requesting for new scrapers</li>
<br>

# Ground Rules
### Expectations from contributors
All contributors must communicate respectfully with other contributors and Scrapera users. Thorough testing of code along with proper documentation is expected from all contributors is expected before merging. 
#####Responsibilities
* Ensure cross-platform compatibility for every change that's accepted. Windows, Mac, Debian & Ubuntu Linux.
* Create issues for any major changes and enhancements that you wish to make. Discuss things transparently and get community feedback.
* Ensure optimality of code
* Ensure that no selenium or webdriver based tools are used
* Don't add any classes to the codebase unless absolutely needed.
* Keep feature versions as small as possible, preferably one new feature per version.
* Be welcoming to newcomers and encourage diverse new contributors from all backgrounds. See the [Python Community Code of Conduct](https://www.python.org/psf/codeofconduct/).

# Getting started

For something that is bigger than a one or two line fix:

1. Create your own fork of the code
2. Do the changes in your fork
3. If you like the change and think the project could use it then be sure you have followed the code style for the project.
4. Create a pull request

# Format for addition of a scraper
1. Ensure that you are writing optimized code and following PEP8 guidelines
2. Your code must follow the format of a single class with a main callable function for every scraper that you add
3. All request calls should be made as asynchronous as possible
4. Callable functions must be properly documented and all parameters should be explained
5. You must add a test file under the domain directory to display how the scraper can be instantiated and executed
6. You must add your scraper/s to the list of scrapers in the `README` file before initiating a pull request

# How to report a bug

<b>If you find a security vulnerability, do NOT open an issue. Email scraperadev@gmail.com instead.</b>

Any security issues should be submitted directly to scraperadev@gmail.com

In order to determine whether you are dealing with a security issue, ask yourself these two questions:
* Can I access something that's not mine, or something I shouldn't have access to?
* Can I disable something for other people?

If the answer to either of those two questions are "yes", then you're probably dealing with a security issue. Note that even if you answer "no" to both questions, you may still be dealing with a security issue, so if you're unsure, just email us.

### How to file a bug report

 When filing an issue, make sure to answer these five questions:

1. What version of Python are you using?
2. What operating system and processor architecture are you using?
3. What did you do?
4. What did you expect to see?
5. What did you see instead?

# Suggest a feature or enhancement

If you find yourself wishing for a module that doesn't exist in Scrapera, you are probably not alone. There are bound to be others out there with similar needs. Many of the modules that Scrapera has today have been added because our users saw the need. Open an issue on our issues list on GitHub which describes the feature you would like to see, why you need it, and how it should work.

# Code review process

The core team looks at Pull Requests on a regular basis.

After feedback has been given we expect responses within two weeks. After two weeks we may close the pull request if it isn't showing any activity.