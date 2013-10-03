#!/usr/bin/env python
# encoding=utf-8

import os
import sys
import uuid
from flask import Flask, render_template, request, send_file
import concatss

INPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/input'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/output'

IMAGE_NAME_PREFIX = 'image'
ACCEPTABLE_IMAGE_COUNT = 100

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("top.html")

@app.route("/concatenated/<concatenated_id>", methods=["GET"])
def concatenated(concatenated_id):
    concatenated_filename = OUTPUT_DIR + '/' + concatenated_id
    return send_file(concatenated_filename, mimetype='image/jpeg')

@app.route("/upload", methods=["POST"])
def upload():
    if request.method == 'POST':
        received_filenames = []
        for index in range(1, ACCEPTABLE_IMAGE_COUNT):
            possible_received_file = IMAGE_NAME_PREFIX + '%02d' % index
            if request.files.get(possible_received_file):
                received_file = request.files[possible_received_file]
                output_filename = INPUT_DIR + '/' + str(uuid.uuid4())
                received_file.save(output_filename)
                received_filenames.append(output_filename)
        if len(received_filenames) < 2:
            return "not enough images specified."

        concatenated_id = str(uuid.uuid4())
        concatenated_filename = OUTPUT_DIR + '/' + concatenated_id

        concat = concatss.ConcatScreenShot()
        concatenated_image = concat.concatenate_images(
                received_filenames, concatenated_filename)

        if concatenated_image:
            concatenated_url = "/concatenated/%s" % concatenated_id
            response = "<a href=\"%s\">%s</a>" % (
                    concatenated_url, concatenated_url)
        else:
            response = "could not concatenate screenshot from uploaded files."

        return response
    return "request method not allowed."

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
