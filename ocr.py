#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Helper"""

import argparse
import logging
from logging import Formatter, FileHandler
from PIL import Image, ImageFilter, ImageDraw
import tesseract
from cStringIO import StringIO
import requests
import database
import json
from os import path
import contextlib
import tempfile
from wand.image import Image as WandImage


class DownloadError(Exception):
    pass


def process_image(url, lang="eng", store_data=False):
    with download_file(url) as imageFile:
        if is_pdf(imageFile):
            image = pdf_to_image(imageFile)
        else:
            image = Image.open(imageFile)

        with image:
            num_pages = get_page_count(image)
            
            # TODO resize to minimum size to improve ocr result
            #image.resize(size, Image.ANTIALIAS)
            #exit(-1)

            all_text = ""
            boxes = []

            # handle multi page images (i.e. tiffs)
            print "Num pages: ", num_pages

            wrapper = tesseract.TesseractWrapper(lang, None)

            for page in range(0, num_pages):
                image.seek(page)
                image_page = image.convert('L')

                text, box_text = wrapper.get_image_data(image, page) #tesseract.get_image_data(image_page, lang, page)
                text = text.strip()
                box_text = box_text.strip()

                for line in box_text.splitlines():
                    (char, x1, y1, x2, y2, page_num) = line.split()
                    # convert from bottom left to top left origin
                    boxes.append((char, (int(x1), image.height - int(y1), int(x2), image.height - int(y2), int(page_num))))

                all_text += text

                #draw boxes on image
                #highlight_image(image, boxes)
                #image.show()

            if store_data:
                boxes_json = json.dumps(boxes, ensure_ascii=False)
                database.save_ocr_metadata(url, all_text, boxes_json)

            return (all_text, boxes)


def highlight_image(image, bounding_boxes):
    #draw boxes on image
    draw = ImageDraw.Draw(image)

    #print bounding_boxes
    for _, (x1, y1, x2, y2, _) in bounding_boxes:
        #print (x1, y1), (x2, y2)
        draw.rectangle(((x1, y1), (x2, y2)), outline="blue")


def download_file(url):
    try:
        if path.isfile(url):
            return open(url, 'rb')
        else:
            #, headers={'User-Agent': 'OCR Server 1.0'}
            data = requests.get(url).content
            return contextlib.closing(StringIO(data))
    except Exception as e:
        raise DownloadError("Failed to download image from url: %s, error: %s" % (url, e))


def is_pdf(aFile):
    header = str(aFile.read(4)) 
    aFile.seek(0)
    return header == "%PDF"


def pdf_to_image(imageFile):
    # Open from filename since opening as file handle means the 
    # format isn't detected as pdf
    with WandImage(filename=imageFile.name, resolution=400) as wand_image:
        # tif written can't be read by Pillow so use gif instead which also supports multi-page
        return Image.open(StringIO(wand_image.make_blob(format='gif')))


def get_page_count(image):
    return getattr(image, 'n_frames', 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image_url')
    parser.add_argument('--lang', default='eng')
    parser.add_argument('--store-data', action='store_true', help='Save the ocr meta data in the database')
    args = parser.parse_args()

    url = args.image_url
    if path.isfile(url):
        url = path.abspath(url)

    text, boxes = process_image(url, lang=args.lang, store_data=args.store_data)
    print text 
    print "-----------"
    print boxes


if __name__ == '__main__':
    main()

