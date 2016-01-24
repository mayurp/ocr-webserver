#!/usr/bin/env python

"""Database Helper"""


from PIL import Image
from PIL import ImageFilter
from StringIO import StringIO
import os
import requests
import logging
from logging import Formatter, FileHandler
from flask_sqlalchemy import SQLAlchemy
import flask.ext.whooshalchemy as whooshalchemy
import datetime
import server

server.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.sqlite'
server.app.config['WHOOSH_BASE'] = 'db/whoosh'
server.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(server.app)

class OcrMetaData(db.Model):
    __searchable__ = 'text'

    image_url = db.Column(db.String, primary_key=True)
    text = db.Column(db.Text)
    bounding_boxes = db.Column(db.String)
    created = db.Column(db.DateTime, default=datetime.datetime.now())
    
    def __init__(self, image_url, text, bounding_boxes):
        self.image_url = image_url
        self.text = text
        self.bounding_boxes = bounding_boxes

    def __repr__(self):
        return '<OcrMetaData %r>' % (self.image_url)

db.create_all()
whooshalchemy.whoosh_index(server.app, OcrMetaData)


def save_ocr_metadata(image_url, text, bounding_boxes):
    existing_record = OcrMetaData.query.get(image_url)
    if existing_record:
        existing_record.text = text
        existing_record.bounding_boxes = bounding_boxes
        existing_record.created = datetime.datetime.now()
    else:
        db.session.add(OcrMetaData(image_url, text, bounding_boxes))
    db.session.commit()

def query_ocr_metadata(keyword, page, page_size):
    return OcrMetaData.query.whoosh_search('keyword OR blah')
    #return OcrMetaData.query.all()
