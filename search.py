#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Search"""


import os
import logging
from logging import Formatter, FileHandler
import database
from PIL import Image
import argparse
import re
import json
import ocr
import xml.etree.ElementTree as etree
import itertools
import operator
from xml.dom import minidom

from pyparsing import *


# Define search DSL (keywords with AND OR expressions)

unicode_printables = u''.join(unichr(c) for c in xrange(65536) if not unichr(c).isspace())

QUOTED = quotedString.setParseAction(removeQuotes)
OAND = CaselessLiteral("AND")
OOR = CaselessLiteral("OR")
ONOT = Literal("-")
WWORD = ~OAND + ~OOR + ~ONOT + Word(unicode_printables.replace("(", "").replace(")", ""))
TERM = (QUOTED | WWORD)
EXPRESSION = operatorPrecedence(TERM,
    [
    (ONOT, 1, opAssoc.RIGHT),
    (Optional(OAND, default="AND"), 2, opAssoc.LEFT),
    (OOR, 2, opAssoc.LEFT)
    ])

QUERY_PARSER = OneOrMore(EXPRESSION) + StringEnd()


class InvalidQuerySyntax(Exception):
    pass


def flatten(x):
    if type(x) is list:
        l = []
        for i in x:
            l += flatten(i)
        return l
    else:
        return [x]


def get_keywords(query):
    tokens = flatten(query)
    return tokens[0::2]


# Return search results as list of tuples in the form:
#            [
#               ( image_url,  [keyword_1, [(x1, y1, x2, y2, page)]], [keyword_2, ...] ),
#               ..
#             ]
def search(query, page=1, page_size=10):
    try:
        parsed_query = QUERY_PARSER.parseString(query).asList()
    except Exception, e:
        raise InvalidQuerySyntax("Invalid query syntax:  %s", e.message)

    logging.debug("Parsed Query: %s", unicode(parsed_query))
    keywords = get_keywords(parsed_query)

    # Get list of OcrMetaData records
    records = database.query_ocr_metadata(parsed_query, page, page_size)

    # find keyword bounds
    results = []
    for record in records: 
        # Strip whitespace and 
        text = re.sub(r"\s", "", record.text)
        bounding_boxes = json.loads(record.bounding_boxes)
        # Find positions of keywords
        image_results = []
        for keyword in keywords:
            # Get start and end position of keyword
            positions = [(match.start(), len(keyword)) for match in re.finditer(re.escape(keyword), text, re.IGNORECASE | re.UNICODE)]
            # Get bounding box of each character
            keyword_char_boxes = [bounding_boxes[start:start+length] for start, length in positions]

            keyword_boxes = []
            for word_boxes in keyword_char_boxes:
                word_boxes = [box for _, box in word_boxes]
                word_boxes_by_page = group_boxes_by_page(word_boxes)
                for word_boxes_for_page in word_boxes_by_page:
                    keyword_boxes += [merge_bounding_boxes(word_boxes_for_page)]

            image_results += [(keyword, keyword_boxes)]

        results += [(record.image_url, image_results)]
    return results


# Tale list of boxes and return list of lists grouped by page
def group_boxes_by_page(boxes):
    return [list(group) for key, group in itertools.groupby(boxes, operator.itemgetter(4))]


# Merge boxes in the form (x1, y1, x2, y2) into 1 box
def merge_bounding_boxes(boxes):
    x1_list = [b[0] for b in boxes]
    y1_list = [b[1] for b in boxes]
    x2_list = [b[2] for b in boxes]
    y2_list = [b[3] for b in boxes]
    return min(x1_list), min(y1_list), max(x2_list), max(y2_list), boxes[0][4]


def search_results_as_xml(query, page=1, page_size=10):
    results = search(query, page, page_size)
    return search_results_to_xml(results, query, page, page_size)


def search_results_to_xml(results, query, page=1, page_size=10):
    root = etree.Element('search_result', records_found=str(len(results)), page=str(page), page_size=str(page_size), keywords=query)
    for image_url, image_results in results:
        imageElem = etree.SubElement(root, 'image', url=image_url)
        for keyword, boxes in image_results:
            for x1, y1, x2, y2, page in boxes:
                etree.SubElement(imageElem, 'match_spot', x1=str(x1)+'px', y1=str(y1)+'px', x2=str(x2)+'px', y2=str(y2)+'px', page=str(page+1))

    return etree.tostring(root, encoding="utf-8")


def prettify_xml(xml_str):
    parsed = minidom.parseString(xml_str)
    return parsed.toprettyxml(indent="\t")

# For debugging bounding box data
def debug_show_search_result(image_url, boxes):    
    with ocr.download_file(image_url) as imageFile:
        with ocr.get_image(imageFile) as image:
            num_pages = ocr.get_page_count(image)
            for page in range(0, num_pages):
                image.seek(page)
                ocr.highlight_keywords(image, boxes, page)
                image.show()


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword')
    parser.add_argument('--show', action='store_true', help="Show first image result with bounding boxes")
    args = parser.parse_args()

    results = search(unicode(args.keyword, 'utf-8'))

    if len(results) <= 0:
        logging.info("No results")
        return

    logging.info("Found %d results:", len(results))
    #logging.debug(print results)

    # for image_url, boxes in results:
    #     logging.info(image_url + ":\n")
    #     for keyword, box in boxes:
    #         logging.info("\t %s : %s", keyword, box)

    xml_str = search_results_to_xml(results, unicode(args.keyword, 'utf-8'))
    logging.debug(prettify_xml(xml_str))


    if args.show:
        logging.info("Showing first result image:")
        image_url, boxes = results[0]
        debug_show_search_result(image_url, boxes)


if __name__ == '__main__':
    main()
