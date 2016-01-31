FROM debian:latest

MAINTAINER Mayur Patel

#RUN apt-get install -y software-properties-common
#RUN add-apt-repository universe

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

RUN apt-get install -y libleptonica-dev imagemagick sqlite
# Tesseract + laguage packs

#libjpeg8-dev # ubuntu

RUN apt-get install -y libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk
RUN apt-get install -y  libtesseract3 libtesseract-dev tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-tra tesseract-ocr-chi-sim

RUN pip install Flask==0.10.1
RUN pip install Flask-SQLAlchemy==2.1
RUN pip install Pillow==3.1.0

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Expose ports
EXPOSE 80

#ENTRYPOINT python
CMD python server.py --host=0.0.0.0 --port=80 #--debug
