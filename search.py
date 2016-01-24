#!/usr/bin/env python

"""OCR Search"""


import os
import requests
import logging
from logging import Formatter, FileHandler
import database
import argparse

def search(keywords, page=1, page_size=10):
	return database.query_ocr_metadata(keywords, page, page_size)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('keyword')
    args = parser.parse_args()

    print search(args.keyword)
