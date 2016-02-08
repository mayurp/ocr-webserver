#!/usr/bin/env python
# -*- encoding: utf-8-*-

"""Database Helper"""

import os
import logging
from logging import Formatter, FileHandler
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
import datetime
from sqlalchemy import Column, Integer, String, Text, UnicodeText, DateTime, or_, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import escape_like


if not os.path.exists("db"):
    os.makedirs("db")

Base = declarative_base()
engine = sqlalchemy.create_engine('sqlite:///db/ocr.sqlite', echo=True)
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


def query_ocr_metadata(parsed_query, page, page_size):
    offset = page_size * max(0, (page - 1))
    query_filter = get_filter(parsed_query)
    sql_query = session.query(OcrMetaData).filter(query_filter).limit(page_size).offset(offset)
    #print str(sql_query)
    return sql_query.all()


# Turn parsed query into sqlalchemy filter
def get_filter(l):
    if type(l) is list:
        if len(l) == 1:
            return get_filter(l[0])
        else:
            op_str = l[1]
            if op_str == "AND":
                op = and_
            else: #OR
                op = or_

            args = []
            for e in l[0::2]:
                print e
                args += [get_filter(e)]
            return op(*args)
    else:
        return OcrMetaData.text.like("%" + escape_like(l) + "%")
