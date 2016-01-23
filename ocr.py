#!/usr/bin/env python

import pytesseract
from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
import os
import requests
import logging
from logging import Formatter, FileHandler

class DownloadError(Exception):
    pass

def process_image(url, lang="eng"):
    imageFile = download_file(url)
    image = Image.open(imageFile)
    image = image.convert('L')
    #    image.resize(size, Image.ANTIALIAS)
    #image.show()
    return pytesseract.image_to_string(image, lang=lang)

def download_file(url):
    try:
        return StringIO(requests.get(url).content)
    except Exception as e:
        raise DownloadError("Failed to download image from url: %s, error: %s" & (url, e.message))

def main():
    pass

if __name__ == '__main__':
    main()
