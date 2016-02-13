#!/usr/bin/env python
# -*- encoding: utf-8-*-

import csv
import sys
import urllib2
import json
import grequests
import logging
import time

# Batch test REST API with .csv of image urls


host="http://192.168.99.100"
#host="http://127.0.0.1:5000"

urls = []
with open(sys.argv[1], 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        urls += [row[0]]



# A list to hold our things to do via async
done_items = []


# A simple task to do to each response object
def do_something(response, **kwargs):
    print "Response: %d" % response.status_code
    print response.request.headers
    #headers = json.loads(str(response.request.headers))
    print "id:", response.request.headers['id']
    print "url:", response.request.headers['url']
    print "elapsed:", time.time() - response.request.headers['start']
    print "---------------"
    global done_items
    done_items += [response.request.headers['id']]
    #print "url: %s" % response.url
    #print response.content

def exception_handler(request, exception):
    print "Request failed: ", request, exception

async_list = []
#urls = urls[0:10]

for i, url in enumerate(urls):
    data='{"image_url" : "%s", "lang" : "eng+chi_tra" }' % url
    headers = {'Content-Type' : 'application/json', 'start' : time.time(), "id" : i, 'url' : url }
    action_item = grequests.post(host + "/ocr", data=data, headers=headers, timeout=600, hooks={'response' : do_something})
    # Add the task to our list of things to do via async
    async_list.append(action_item)


start = time.time()

# Do our list of things to do via async
grequests.map(async_list, exception_handler=exception_handler)

elapsed = time.time()
elapsed = elapsed - start
print "Time spent: ", elapsed

for i, url in enumerate(urls):
    if i not in done_items:
        print "No result for item %d: %s" % (i, url)

