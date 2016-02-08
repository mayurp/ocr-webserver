FROM debian:latest

MAINTAINER Mayur Patel

RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential

RUN apt-get install -y libleptonica-dev imagemagick sqlite

# ubuntu
#libjpeg8-dev
RUN apt-get install -y libtiff5-dev libjpeg62-turbo-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk

# Tesseract + laguage packs
RUN apt-get install -y  libtesseract3 libtesseract-dev tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-tra tesseract-ocr-chi-sim

RUN pip install Pillow==3.1.0
RUN pip install SQLAlchemy==1.0.11
RUN pip install Wand==0.4.2
#RUN pip install requests==2.9.1
RUN pip install tornado==4.3
RUN pip install tornado-smack==1.0.4
RUN pip install futures

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

# Expose ports
EXPOSE 80

# ENTRYPOINT python
CMD python server.py --port=80
