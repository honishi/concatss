#!/usr/bin/env python
# encoding=utf-8

import os
import uuid
import threading
from flask import Flask, render_template, request, send_file
import concatss

INPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/input'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__)) + '/output'

IMAGE_NAME_PREFIX = 'image'
ACCEPTABLE_IMAGE_COUNT = 10

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("top.html")


@app.route("/concatenated/<concatenated_id>", methods=["GET"])
def concatenated(concatenated_id):
    concatenated_filename = OUTPUT_DIR + '/' + concatenated_id
    status_filename = concatenated_filename + '.status'
    if os.path.exists(status_filename):
        logfile = open(status_filename)
        log = logfile.read()
        logfile.close()
        meta = metatag_for_redirect(concatenated_id)
        return "{}\n{}".format(log, meta)
    elif not os.path.exists(concatenated_filename):
        return "failed."
    return send_file(concatenated_filename, mimetype='image/jpeg')


@app.route("/upload", methods=["POST"])
def upload():
    if request.method != 'POST':
        return "request method not allowed."

    received_filenames = []
    for idx in range(1, ACCEPTABLE_IMAGE_COUNT):
        # get image as FileStorage type
        possible_image_name = IMAGE_NAME_PREFIX + '{0:02d}'.format(idx)
        received_filestorage = request.files[possible_image_name]

        # try to flush it
        output_filename = INPUT_DIR + '/' + str(uuid.uuid4())
        received_filestorage.save(output_filename)
        if os.path.getsize(output_filename):
            received_filenames.append(output_filename)
        else:
            os.remove(output_filename)

    if len(received_filenames) < 2:
        return "not enough images specified."

    concatenated_id = str(uuid.uuid4())
    concat_thread = threading.Thread(target=concat, args=(concatenated_id, received_filenames))
    concat_thread.start()

    return "uploaded.{}".format(metatag_for_redirect(concatenated_id))


def metatag_for_redirect(concatenated_id):
    url = "/concatenated/{}".format(concatenated_id)
    return "<meta http-equiv=\"refresh\" content=\"2;URL={}\">".format(url)


def concat(concatenated_id, received_filenames):
    concatenated_filename = OUTPUT_DIR + '/' + concatenated_id
    concatss.concatenate_images(received_filenames, concatenated_filename, True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
