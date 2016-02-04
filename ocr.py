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
from wand.image import Image as WandImage
import re


class DownloadError(Exception):
    pass


def process_image(url, lang="eng", store_data=False):
    with download_file(url) as imageFile:
        with get_image(imageFile) as image:
            num_pages = get_page_count(image)

            all_text = ""
            boxes = []

            # handle multi page images (i.e. tiffs)
            logging.info("Num pages: %s", num_pages)

            wrapper = tesseract.TesseractWrapper(lang, None)

            for page in range(0, num_pages):
                image.seek(page)
                w, h = image.size

                scaled_image = image.convert('L')                
                # TODO resize to minimum size to improve ocr result
                #scaled_image = scaled_image.resize((w * 2, h * 2), Image.ANTIALIAS)
                scaled_w, scaled_h = scaled_image.size

                logging.info("Running tesseract on page: %s", page)

                text, box_text = wrapper.get_image_data(scaled_image, page)
                
                text = text.strip()
                box_text = box_text.strip()

                for line in box_text.splitlines():
                    token, x1, y1, x2, y2, page_num = line.split()
                    # Scale back according to original image size
                    x1 = (int(x1) * w) / scaled_w
                    y1 = (int(y1) * h) / scaled_h
                    x2 = (int(x2) * w) / scaled_w
                    y2 = (int(y2) * h) / scaled_h
                    # convert from bottom left to top left origin
                    box = (x1, h - y1, x2, h - y2, int(page_num)) 
                    # Tesseract sometimes returns multiple characters per token.
                    for char in token: 
                        boxes.append((char, box))

                all_text += text

                #draw boxes on original image
                #highlight_image(image, boxes)
                #image.show()
            
            # Verify text matches boxes indices
            stripped_text = re.sub(r"\s", "", all_text)
            boxes_text = u"".join([b[0] for b in boxes])

            if stripped_text != boxes_text:
                logging.error("lengths - (text, boxes, boxes_text) : (%d, %d, %d)", len(stripped_text), len(boxes), len(boxes_text))
                #raise Exception("tesseract text does not match boxes text")

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
            logging.info("Downloading file: %s", url)
            response = requests.get(url)
            if response.status_code == 200:
                return contextlib.closing(StringIO(response.content))
            else:
                raise DownloadError("Failed to download image: %s, response: %d" % (url, response.status_code))
    except Exception as e:
        raise DownloadError("Failed to download image: %s, error: %s" % (url, e))


def get_image(imageFile):
    if is_pdf(imageFile):
        return pdf_to_image(imageFile)
    else:
        return Image.open(imageFile)


def is_pdf(aFile):
    header = str(aFile.read(4)) 
    aFile.seek(0)
    return header == "%PDF"


def pdf_to_image(imageFile):
    # Open from filename since opening as file handle means the 
    # format isn't detected as pdf
    logging.info("Converting pdf to image")
    with WandImage(filename=imageFile.name, resolution=300) as wand_image:
        # tif written can't be read by Pillow so use gif instead which also supports multi-page
        #print wand_image.size
        data = StringIO(wand_image.make_blob(format='gif'))
        return Image.open(data)


def get_page_count(image):
    return getattr(image, 'n_frames', 1)


def main():
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image_url')
    parser.add_argument('--lang', default='eng')
    parser.add_argument('--store-data', action='store_true', help='Save the ocr meta data in the database')
    args = parser.parse_args()

    url = args.image_url
    if path.isfile(url):
        url = path.abspath(url)

    text, boxes = process_image(url, lang=args.lang, store_data=args.store_data)
    logging.info(text)
    logging.info("---------------")
    logging.info(boxes)


if __name__ == '__main__':
    main()

