#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Search"""


import os
import requests
import logging
from logging import Formatter, FileHandler
import database
#from database import OcrMetaData
from PIL import Image
import argparse
import re
import json
import ocr
import xml.etree.ElementTree as etree

def search(keywords, page=1, page_size=10):
    pages = database.query_ocr_metadata(keywords, page, page_size)

    # find keyword bounds
    results = []
    for record in pages.items:
        text = re.sub(r"\s", "", record.text)
        bounding_boxes = json.loads(record.bounding_boxes)
        positions = [(match.start(), len(keywords))  for match in re.finditer(re.escape(keywords), text)]
        
        keyword_char_boxes = [bounding_boxes[start:start+length] for start, length in positions]
        keyword_char_boxes = [item for sublist in keyword_char_boxes for item in sublist]
        
        # TODO merge overlapping bounding boxes for keywords ?
        results += [(record.image_url, keyword_char_boxes)]

    return results


def search_results_as_xml(keywords, page, page_size):
    results = search(keywords, page, page_size)

    root = etree.Element('search_result', recordsfound=str(len(results)), page=str(page), page_size=str(page_size), keywords=keywords)
    #doc = etree.ElementTree(root)
    for r in results:
        imageElem = etree.SubElement(root, 'image', url=r[0])
        boxes = r[1]
        for _, (x1, y1, x2, y2, _) in boxes:
            boxElem = etree.SubElement(imageElem, 'match_spot', x1=str(x1), y1=str(y1), x2=str(x2), y2=str(y2)) 

    return etree.tostring(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword')
    args = parser.parse_args()

    results = search(unicode(args.keyword, 'utf8'))

    if len(results) <= 0:
        print "No results"
        return

    print "First result: "

    image_url, boxes = results[0]

    print image_url, boxes

    with ocr.download_file(image_url) as imageFile:
        image = Image.open(imageFile)
        ocr.highlight_image(image, boxes)
        image.show()

    #print search_results_to_xml((image_url, boxes))

if __name__ == '__main__':
    main()
