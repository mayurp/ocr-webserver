# Summary

An OCR web service implemented in python.

# Setup

## Option 1. Using Docker 

It is recommended to run the service inside a [Docker](#https://www.docker.com) container as it automates the installation of all the dependencies and you can sure it is running in the same environment as it was tested on.

To build the docker image:
	
	cd icicle-ocr
	docker build -t ocr-webserver .

To run the container (this will start the server):
	
	docker run  -p 80:80 -i -t ocr-webserver 

Please refer to the Dockerfile for details of the container.

## Option 2. Manual Installation

If you do not wish to use Docker you will need to instead install all the dependencies specified in the Dockerfile yourself.

Also, you should use python virtualenv:
	
	sudo pip install virtualenv
	
	cd icicle-ocr
	virtualenv env
	source env/bin/activate
	pip install -r requirements.txt


### Start the server

	./server.py

You can use run `./server.py --help` for startup options.


## Testing the OCR API:

Please note you should change the ip address and port according to your setup.

English:
	
	curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
	    \"image_url\":\"http://bit.ly/ocrimage\",
	    \"lang\":\"eng\"
	}" 'http://127.0.0.1:5000/v1/ocr'


English and Traditional Chinese 

	curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
	    \"image_url\":\"https://i.ytimg.com/vi/xEnutX1zZfA/maxresdefault.jpg\",
	    \"lang\":\"eng+chi_tra\"
	}" 'http://127.0.0.1:5000/v1/ocr'


For English and Simplified Chinese use `"lang": "eng+chi_sim"`

## Testing the Search API:

	curl --include --request GET --header "Content-Type: application/json" --data-binary "{  
	    \"keywords\":\"全文\",
	    \"page\": 1,
	    \"page_size\": 10
	}" 'http://127.0.0.1:5000/v1/search'


## Standalone Testing

To test OCR directly, without the server:

	./ocr.py https://i.ytimg.com/vi/xEnutX1zZfA/maxresdefault.jpg --store-data

The image will then be searchable:

	./search.py 全文
	
To run these tests in the docker container simply use `docker exec`. For example:

	docker exec <CONTAINER-ID> ./search.py "全文"