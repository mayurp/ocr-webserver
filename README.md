## Install packages 

On OSX use the command "brew install" or on Ubuntu or Debian use "sudo apt-get install"

- tesseract 
- imagemagick
- sqlite


## Setup python environment

cd icicle-ocr
 
sudo pip install virtualenv
	
virtualenv env

source env/bin/activate

pip install -r requirements.txt

## Run the server

./server.py


## Test OCR REST API:

# English
curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
    \"image_url\":\"http://bit.ly/ocrimage\",
    \"lang\":\"eng\"
}" 'http://127.0.0.1:5000/v1/ocr'

# English + Chinese
curl --include --request POST --header "Content-Type: application/json" --data-binary "{  
    \"image_url\":\"https://i.ytimg.com/vi/xEnutX1zZfA/maxresdefault.jpg\",
    \"lang\":\"eng+chi_tra\"
}" 'http://127.0.0.1:5000/v1/ocr'



## Test Search REST API:

curl --include --request GET --header "Content-Type: application/json" --data-binary "{  
    \"keywords\":\"you\",
    \"page\": 1,
    \"page_size\": 10
}" 'http://127.0.0.1:5000/v1/search'



# TODOS
- Pdf support (both text based and scanned)
- Search for multiple keywords with AND / OR expressions
- Use libccv to improve speed and accuracy of Chinese character recognition