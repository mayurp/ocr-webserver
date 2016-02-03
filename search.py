#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Search"""


import os
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

    root = etree.Element('search_result', records_found=str(len(results)), page=str(page), page_size=str(page_size), keywords=keywords)
    #doc = etree.ElementTree(root)
    for url, boxes in results:
        imageElem = etree.SubElement(root, 'image', url=url)
        for _, (x1, y1, x2, y2, page) in boxes:
            etree.SubElement(imageElem, 'match_spot', x1=str(x1)+'px', y1=str(y1)+'px', x2=str(x2)+'px', y2=str(y2)+'px', page=str(page+1))

    return etree.tostring(root)


# For debugging bounding box data
def debug_show_search_result(image_url, boxes):    
    with ocr.download_file(image_url) as imageFile:
        with ocr.get_image(imageFile) as image:
            num_pages = ocr.get_page_count(image)
            for page in range(0, num_pages):
                image.seek(page)
                ocr.highlight_image(image, boxes)
                image.show()


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword')
    parser.add_argument('--show', action='store_true', help="Show first image result with bounding boxes")
    args = parser.parse_args()

    results = search(unicode(args.keyword, 'utf-8'))

    if len(results) <= 0:
        print "No results"
        return

    print "Found ", len(results), " results:"
    for  image_url, boxes in results:
        print image_url, boxes

    if args.show:
        print "Showing first result image: "
        image_url, boxes = results[0]
        debug_show_search_result(image_url, boxes)

if __name__ == '__main__':
    main()
