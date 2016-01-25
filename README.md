## Install packages 

On OSX use the command "brew install" or on Ubuntu or Debian use "sudo apt-get install"

tesseract 
sqlite
imagemagick


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