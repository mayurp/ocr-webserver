#!/usr/bin/env python

"""Tesseract Wrapper"""

from PIL import Image
import subprocess
import os
from os import path
import shlex
import shutil
import tempfile

class TesseractError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.args = (status, message)


def run_tesseract(input_filename, output_filename_base, lang=None, boxes=False, config=None):
    '''
    runs the command:
        `tesseract_cmd` `input_filename` `output_filename_base`
    
    returns the exit status of tesseract, as well as tesseract's stderr output

    '''
    command = ["tesseract", input_filename, output_filename_base]
    
    if lang is not None:
        command += ['-l', lang]

    if boxes:
        command += ['batch.nochop', 'makebox']
        
    if config:
        command += shlex.split(config)
    
    proc = subprocess.Popen(command,
            stderr=subprocess.PIPE)
    return (proc.wait(), proc.stderr.read())


def get_errors(error_string):
    '''
    returns all lines in the error_string that start with the string "error"

    '''

    lines = error_string.splitlines()
    error_lines = tuple(line for line in lines if line.find('Error') >= 0)
    if len(error_lines) > 0:
        return '\n'.join(error_lines)
    else:
        return error_string.strip()


# Returns tuple of image text and  optionally bounding boxes (if requestions)
def get_image_data(image, lang=None, boxes=False, config=None):
    if len(image.split()) == 4:
        # In case we have 4 channels, lets discard the Alpha.
        # Kind of a hack, should fix in the future some time.
        r, g, b, _ = image.split()
        image = Image.merge("RGB", (r, g, b))

    temp_dir = tempfile.mkdtemp()

    input_file_name = path.join(temp_dir, 'input.bmp')
    output_file_name_base = path.join(temp_dir, 'output')

    image.save(input_file_name)
    
    try:    
        status, error_string = run_tesseract(input_file_name,
                                             output_file_name_base,
                                             lang=lang,
                                             boxes=boxes,
                                             config=config)
        if status:
            errors = get_errors(error_string)
            raise TesseractError(status, errors)
        
        with open(output_file_name_base + ".txt", 'r') as text_file:
            text = text_file.read().strip()
            box_data = None
            if boxes:
                with open(output_file_name_base + ".box", 'r') as box_file:
                    box_data = box_file.read().strip()
            return (text, box_data)
    finally:
        shutil.rmtree(temp_dir)
