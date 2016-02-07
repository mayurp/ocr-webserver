#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""Database Helper"""

import os
import logging
from logging import Formatter, FileHandler
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Column, Integer, String, Text, UnicodeText, DateTime
from sqlalchemy.orm import sessionmaker


if not os.path.exists("db"):
    os.makedirs("db")

Base = declarative_base()
engine = sqlalchemy.create_engine('sqlite:///db/ocr.sqlite')
# Construct a sessionmaker object
Session = sessionmaker()
# Bind the sessionmaker to engine
Session.configure(bind=engine)
session = Session()


class OcrMetaData(Base):
    __tablename__ = 'ocr_data'

    image_url = Column(String, primary_key=True)
    text = Column(String)
    bounding_boxes = Column(String)
    created = Column(DateTime, default=datetime.datetime.now())

    def __init__(self, image_url, text, bounding_boxes):
        self.image_url = image_url
        self.text = text
        self.bounding_boxes = bounding_boxes

    def __repr__(self):
        return '<OcrMetaData %r>' % self.image_url


# Create all the tables in the database which are
# defined by Base's subclasses such as User
Base.metadata.create_all(engine)


def save_ocr_metadata(image_url, text, bounding_boxes):
    logging.info("Saving metadata to database for: %s", image_url)
    existing_record = session.query(OcrMetaData).get(image_url)
    if existing_record:
        existing_record.text = text
        existing_record.bounding_boxes = bounding_boxes
        existing_record.created = datetime.datetime.now()
    else:
        session.add(OcrMetaData(image_url, text, bounding_boxes))
    session.commit()


# TODO whoosh for full text search
def query_ocr_metadata(keyword, page, page_size):
    offset = page_size * max(0, (page - 1))
    return session.query(OcrMetaData).filter(OcrMetaData.text.like("%" + keyword + "%")).limit(page_size).offset(offset).all()
