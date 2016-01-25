## Install these native packages and their dependencies 
(on OSX use "brew install" or on linux "apt-get install")

tesseract 
postgresql or mysql


# Postgresql Setup

cd db
initdb -D data
postgres -D data > logfile 2>&1 &



## Setup python environment

sudo pip install virtualenv
	
virtualenv env

source env/bin/activate

pip install -r requirements.txt






## Run the server


## 
