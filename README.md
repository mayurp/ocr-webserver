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

## Test ocr from command line and print text
./ocr.py [image_url]


# TODOS
- Pdf support (both text based and scanned)
- Search for multiple keywords with AND / OR expressions
- Use libccv to improve speed and accuracy of Chinese character recognition