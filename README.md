# Summary

An OCR web service implemented in python.

# Setup

## Install dependencies 

On OSX you can use "brew install" or on Ubuntu or Debian use "sudo apt-get install" 

- leptonica
- imagemagick
- sqlite

## Install tesseract on OSX:

brew install tesseract --all-languages

## Install tesseract on Debian:

sudo apt-get install libtesseract-dev

sudo apt-get install tesseract-ocr-eng tesseract-ocr-chi-tra tesseract-ocr-chi-sim



## Setup python virtual environment

sudo pip install virtualenv

cd icicle-ocr
 	
virtualenv env

source env/bin/activate

pip install -r requirements.txt


## Run the server

./server.py


## Test OCR REST API:

### English
curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
    \"image_url\":\"http://bit.ly/ocrimage\",
    \"lang\":\"eng\"
}" 'http://127.0.0.1:5000/v1/ocr'


### English and Chinese

curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
    \"image_url\":\"https://i.ytimg.com/vi/xEnutX1zZfA/maxresdefault.jpg\",
    \"lang\":\"eng+chi_tra\"
}" 'http://127.0.0.1:5000/v1/ocr'


## Test Search REST API:

curl --include --request GET --header "Content-Type: application/json" --data-binary "{  
    \"keywords\":\"全文\",
    \"page\": 1,
    \"page_size\": 10
}" 'http://127.0.0.1:5000/v1/search'


## Standalone testing

### To test OCR directly, without the server:

./ocr.py https://i.ytimg.com/vi/xEnutX1zZfA/maxresdefault.jpg --store-data

### The image will then be searchable:

./search.py 全文