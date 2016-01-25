#!/usr/bin/env python

"""OCR Helper"""

import argparse
import logging
from logging import Formatter, FileHandler
from PIL import Image, ImageFilter, ImageDraw
import tesseract
from StringIO import StringIO
import requests
import database
import json


class DownloadError(Exception):
    pass

def process_image(url, lang="eng", store_data=False):
    imageFile = download_file(url)
    image = Image.open(imageFile)
    image = image.convert('L')
    #    image.resize(size, Image.ANTIALIAS)
    #image.show()
    data = tesseract.get_image_data(image, lang=lang, boxes=True)

    text = data[0]
    boxes = []
    for line in data[1].splitlines():
        (char, x1, y1, x2, y2, page) = line.split()
        # convert from bottom left to top left origin
        boxes.append((char, (int(x1), image.height - int(y1), int(x2), image.height - int(y2), int(page))))

    #draw boxes on image
    highlight_image(image, boxes)
    image.show()

    if store_data:
        boxes_json = json.dumps(boxes)
        database.save_ocr_metadata(url, text, boxes_json)

    return (text, boxes)


def highlight_image(image, bounding_boxes):
    #draw boxes on image
    draw = ImageDraw.Draw(image)

    #print bounding_boxes
    for _, (x1, y1, x2, y2, _) in bounding_boxes:
        #print (x1, y1), (x2, y2)
        draw.rectangle(((x1, y1), (x2, y2)), outline="blue")

def download_file(url):
    try:
        return StringIO(requests.get(url).content)
    except Exception as e:
        raise DownloadError("Failed to download image from url: %s, error: %s" & (url, e.message))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image_url')
    parser.add_argument('--lang', default='eng')
    parser.add_argument('--store-data', action='store_true')
    args = parser.parse_args()

    data = process_image(args.image_url, lang=args.lang, store_data=args.store_data)

    #print data[0]
    #print "-----"
    #print data[1]
