#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""OCR Webservice"""

__author__ = "Mayur Patel"


import argparse
import logging
from logging import Formatter, FileHandler
import json
import tornado
import tornado.options
import tornado.httpserver
from tornado.ioloop import IOLoop
from tornado.gen import coroutine
from tornado import web
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from tornado_smack import App
import random, time
import sys
import ConfigParser

import ocr
import search


app = App()



class APIError(web.HTTPError):
    def __init__(self, message, status_code=400):
        web.HTTPError.__init__(self, status_code, reason=message)
        
    # def to_dict(self):
    #     rv = dict(self.payload or ())
    #     rv['error'] = self.message
    #     return rv


# Simple Tornado base handler with error handling
class BaseHandler(tornado.web.RequestHandler):
    def __init__(self,application, request,**kwargs):
        super(BaseHandler,self).__init__(application,request)

    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'text/json')
        self.finish(json.dumps({}))

    #def _handle_request_exception(self, e):
    #    logging.error('error')
        #write_error(self, 500, e)


class DefaultHandler(BaseHandler):
    pass


@app.route("/")
def hello():
    return "OCR Webservice is running"


# Run OCR on provided image and return UT8 text. OCR meta data is persisted  
@app.route('/ocr', methods=["POST"])
def ocr_api(self):
    try:
        request_json = json.loads(self.request.body)
        url = request_json['image_url']
        lang = request_json.get('lang', 'eng')
    except:
        raise APIError("Did you mean to send: {'image_url': 'some_jpeg_url'}")

    try:
        text, _ = ocr.process_image(url, lang, store_data=True)
        # workaround to set charset to utf8
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({"output" : text}, ensure_ascii=False))
    except ocr.DownloadError as e:
        raise APIError(e.message)
    except Exception as e:
        raise APIError("Failed to process image: %s" % e.message, status_code=500)


# Search OCR meta data of processed images
@app.route('/search', methods=["GET", "POST"], handler_bases=(BaseHandler,))
def search_api(self):
    try:
        request_json = json.loads(self.request.body)
        keywords = request_json['keywords']
        page = int(request_json['page'])
        page_size = int(request_json['page_size'])
    except:
        raise APIError("Did you mean to send: {'keywords': 'someword', 'page' : 1, 'page_size' : 10 }")
    try:
        results_xml = search.search_results_as_xml(keywords, page, page_size)
        self.set_header('Content-Type', 'text/xml')
        self.write(results_xml)
    except Exception as e:
        raise APIError("Unexpected error during search: %s" % e.message, status_code=500)


# def ocr_task(url):
#     s = 0
#     for i in range(0, 10000*1000):
#         s += i
#     return s

# @app.route('/test', methods=["GET"], handler_bases=(BaseHandler,))
# @coroutine
# def test_api(self):
#     blah = self.request.body
#     #res = yield self.long_running_task(3)
#     res = yield ocr_executor.submit(long_running_task, 3) 
#     self.write("--test done : %d\n" % res)

# @app.route('/quick', methods=["GET"], handler_bases=(BaseHandler,))
# @coroutine
# def quick_api(self):
#     #blah = self.request.body
#     #search_executor
#     self.write("------ quick done\n") 


# Error handlers

# @app.errorhandler(500)
# def internal_error(error):
#     logging.info(str(error))


# @app.errorhandler(404)
# def not_found_error(error):
#     logging.info(str(error))


# @app.errorhandler(APIError)
# def handle_api_error(error):
#     response = error.to_dict()
#     response.status_code = error.status_code
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
    #parser.add_argument('--host', default="127.0.0.1")
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()

    # Need to reset argv and call tornado's parse options for logging to work correctly
    sys.argv = ""
    tornado.options.parse_command_line()

    #logging.info("Number of cpu cores: %d", proc_count)
    logging.info('Reading config..')
    config = ConfigParser.ConfigParser()
    config.read("config.ini")
    server_processes = int(config.get('server', 'server_processes'))
    ocr_processes = int(config.get('server', 'ocr_processes'))

    # Tornado can't start with multiple processes in debug mode
    if args.debug:
        server_processes = 1


    logging.info('Starting up...')
    application = tornado.web.Application(app.get_routes(), default_handler_class=DefaultHandler, debug=args.debug)
    server = tornado.httpserver.HTTPServer(application)
    server.bind(args.port)

    logging.info("Starting server processes: %d", server_processes)
    server.start(server_processes)    

    #num_ocr_processes = max(1, proc_count / 2)
    #num_search_pocesses = proc_count
    logging.info("OCR process pool size: %d", ocr_processes)
    ocr_executor = ProcessPoolExecutor(ocr_processes)
    #search_executor = ProcessPoolExecutor(num_search_pocesses)
    #logging.info("Search process pool size: %d", num_search_pocesses)

    IOLoop.current().start()
