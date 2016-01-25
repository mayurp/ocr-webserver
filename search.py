#!/usr/bin/env python

"""OCR Search"""


import os
import requests
import logging
from logging import Formatter, FileHandler
import database
from database import OcrMetaData
from PIL import Image
import argparse
import re
import json
import ocr


def search(keyword, page=1, page_size=10):
    pages = database.query_ocr_metadata(keyword, page, page_size)

    # find keyword bounds
    results = []
    for record in pages.items:
        text = re.sub(r"\s", "", record.text)
        bounding_boxes = json.loads(record.bounding_boxes)
        positions = [(match.start(), len(keyword))  for match in re.finditer(re.escape(keyword), text)]
        #print positions
        keyword_char_boxes = [bounding_boxes[start:start+length] for start, length in positions]
        keyword_char_boxes = [item for sublist in keyword_char_boxes for item in sublist]
        #print keyword_char_boxes
        results += [(record.image_url, keyword_char_boxes)]

    return results


# return array o
#def find_char_bounds(text, keyword)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword')
    args = parser.parse_args()

    image_url, boxes = search(args.keyword)[0]

    print boxes

    imageFile = ocr.download_file(image_url)
    image = Image.open(imageFile)
    ocr.highlight_image(image, boxes)
    image.show()
