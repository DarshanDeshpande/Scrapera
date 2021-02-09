from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name="scrapera",
    version="1.1.3",
    description="A universal package of scraper scripts for humans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DarshanDeshpande/Scrapera",
    author="Darshan Deshpande",
    author_email="darshan1504@gmail.com",
    license="MIT",
    python_requires=">=3.6.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["scrapera"],
    package_data={"scrapera": ["*/*"]},
    include_package_data=True,
    install_requires=required,
)
