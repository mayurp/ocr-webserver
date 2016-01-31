# Summary

An OCR web service implemented in python.

# Setup

## Install dependencies 

On OSX you can use "brew install" or on Ubuntu or Debian use "sudo apt-get install" 

- leptonica
- imagemagick
- sqlite
- swig
- opencv

### Install tesseract on OSX:
	brew tap homebrew/science
	brew install opencv
	brew install tesseract --all-languages

### Install tesseract on Ubuntu or Debian:

	sudo apt-get install libtesseract-dev
	sudo apt-get install tesseract-ocr-eng tesseract-ocr-chi-tra tesseract-ocr-chi-sim



### Setup python virtual environment

	sudo pip install virtualenv
	
	cd icicle-ocr
	virtualenv env
	source env/bin/activate
	pip install -r requirements.txt


## Start the server

	./server.py

You can use run `./server.py --help` for startup options.


## OCR API:

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

## Search API:

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