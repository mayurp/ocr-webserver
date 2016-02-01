#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Webservice"""

__author__ = "Mayur Patel"

import argparse
from flask import Flask, jsonify, request, Response
import ocr
#from ocr import DownloadError
import logging
from logging import Formatter, FileHandler
import search

_VERSION = 1

app = Flask(__name__)


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.message
        return rv


@app.route("/")
def hello():
    return "OCR Webservice is running"


# Run OCR on provided image and return UT8 text. OCR meta data is persisted  
@app.route('/v{}/ocr'.format(_VERSION), methods=["POST"])
def ocr_api():
    try:
        url = request.json['image_url']
        lang = request.json.get('lang', 'eng')
    except:
        raise APIError("Did you mean to send: {'image_url': 'some_jpeg_url'}")

    try:
        text, _ = ocr.process_image(url, lang, store_data=True)
        response = jsonify({"output": text})
        # workaround to set charset to utf8
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except ocr.DownloadError as e:
        raise APIError(e.message)
    except Exception as e:
        raise APIError("Failed to process image: %s" % e.message, status_code=500)


# Search OCR meta data of processed images
@app.route('/v{}/search'.format(_VERSION), methods=["GET"])
def search_api():
    try:
        keywords = request.json['keywords']
        page = int(request.json['page'])
        page_size = int(request.json['page_size'])
    except:
        raise APIError("Did you mean to send: {'keywords': 'someword', 'page' : 1, 'page_size' : 10 }")
    try:
        results_xml = search.search_results_as_xml(keywords, page, page_size)
        return Response(results_xml, mimetype='text/xml')
    except Exception as e:
        raise APIError("Unexpected error during search: %s" % e.message, status_code=500)

# Error handlers

@app.errorhandler(500)
def internal_error(error):
    print str(error)


@app.errorhandler(404)
def not_found_error(error):
    print str(error)


@app.errorhandler(APIError)
def handle_api_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

## TODO remove?
# # Catch all unexpected exceptions
# @app.errorhandler(Exception)
# def handle_internal_error(error):
#     response = jsonify("Internal Server Error: %s", error.message)
#     response.status_code = 500 
#     return response


def init_logging(debug=False):
    if not debug:
        file_handler = FileHandler('error.log')
        file_handler.setFormatter(
            Formatter('%(asctime)s %(levelname)s: \
                %(message)s [in %(pathname)s:%(lineno)d]')
        )
        app.logger.setLevel(logging.INFO)
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.info('errors')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true', help="For development only. Allows auto reloading of code")
    parser.add_argument('--host', default="127.0.0.1")
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    init_logging(args.debug)

    app.run(host=args.host, port=args.port, debug=args.debug)
