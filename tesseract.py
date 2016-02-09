#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tesseract 3.04 wrapper
"""

import argparse
import os
import sys
import ctypes
from  PIL import Image
import logging

# Change this according to your platform
if sys.platform == "darwin":
    LIB_NAME = "libtesseract.dylib"
elif sys.platform == 'win':
    LIB_NAME = "libtesseract.dll"
else:
    LIB_NAME = "libtesseract.so"


class TesseractWrapper:
    class _TessBaseAPI(ctypes.Structure): pass
    class _TessResultRenderer(ctypes.Structure) : pass

    def __init__(self, lang, tessdata):
        try:
            tesseract = ctypes.cdll.LoadLibrary(LIB_NAME)
        except Exception, e:
            logging.error("Failed to load '%s: %s'", LIB_NAME, e)
            exit(1)

        tesseract.TessVersion.restype = ctypes.c_char_p
        TessBaseAPI = ctypes.POINTER(self._TessBaseAPI)
        TessResultRenderer = ctypes.POINTER(self._TessResultRenderer)

        tesseract.TessBaseAPICreate.restype = TessBaseAPI

        tesseract.TessBaseAPIDelete.restype = None  # void
        tesseract.TessBaseAPIDelete.argtypes = [TessBaseAPI]

        tesseract.TessBaseAPIInit3.argtypes = [TessBaseAPI,
                                               ctypes.c_char_p, 
                                               ctypes.c_char_p]

        tesseract.TessBaseAPIProcessPages.restype = ctypes.c_bool
        tesseract.TessBaseAPIProcessPages.argtypes = [TessBaseAPI, 
                                                      ctypes.c_char_p,
                                                      ctypes.c_char_p,
                                                      ctypes.c_int,
                                                      TessResultRenderer]

        tesseract.TessBaseAPISetImage.restype = None
        tesseract.TessBaseAPISetImage.argtypes = [TessBaseAPI,
                                                  ctypes.c_void_p, 
                                                  ctypes.c_int, 
                                                  ctypes.c_int, 
                                                  ctypes.c_int, 
                                                  ctypes.c_int]

        tesseract.TessBaseAPIGetUTF8Text.restype = ctypes.c_char_p
        tesseract.TessBaseAPIGetUTF8Text.argtypes = [TessBaseAPI]

        tesseract.TessBaseAPIGetBoxText.restype = ctypes.c_char_p
        tesseract.TessBaseAPIGetBoxText.argtypes = [TessBaseAPI]

        tesseract.TessDeleteText.restype = None
        tesseract.TessDeleteText.argtypes = [ctypes.c_char_p]

        tesseract_version = tesseract.TessVersion()[:4]

        logging.info("Found tesseract-ocr library version %s." % tesseract_version)
        if float(tesseract_version) < 3.02:
            logging.error("C-API is present only in version 3.02!")
            exit(2)

        api = tesseract.TessBaseAPICreate()
        rc = tesseract.TessBaseAPIInit3(api, tessdata, lang)
        if rc:
            tesseract.TessBaseAPIDelete(api)
            logging.error("Could not initialize tesseract.\n")
            exit(3)

        self.tesseract = tesseract
        self.api = api


    def __del__(self):
        if self. tesseract and self.api:
            self.tesseract.TessBaseAPIDelete(self.api)


    # Return tuple of text and bounding boxes
    def get_image_data(self, image, page):
        w, h = image.size
        data = image.tobytes() 
        d = len(data) / (w*h)

        self.tesseract.TessBaseAPISetImage(self.api, ctypes.c_char_p(data), w, h, d, w * d)
        c_text = self.tesseract.TessBaseAPIGetUTF8Text(self.api)
        #self.tesseract.TessDeleteText(c_text)
        text = ctypes.string_at(c_text)

        c_boxes = self.tesseract.TessBaseAPIGetBoxText(self.api, page)
        #self.tesseract.TessDeleteText(c_boxes)
        boxes = ctypes.string_at(c_boxes)

        return unicode(text, 'utf-8'), unicode(boxes, 'utf-8')


def get_image_data(image, lang, page=0):
    tessData = os.environ.get('TESSDATA_PREFIX', None)
    wrapper = TesseractWrapper(lang, tessData)
    return wrapper.get_image_data(image, page)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('imagePath')
    parser.add_argument('--lang', default="eng")
    args = parser.parse_args()

    #if not tessData or path.isdir(tessData):
    #    print("Please set the TESSDATA_PREFIX environment variable")
    #    exit(1)

    image = Image.open(args.imagePath)

    #start = time.time()
    text, boxes = get_image_data(image, args.lang)
    #end = time.time()
    #print(end - start)

    logging.info(text)
    logging.info("-----------")
    logging.info(boxes)


if __name__ == '__main__':
    main()
