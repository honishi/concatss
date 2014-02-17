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
ACCEPTABLE_IMAGE_COUNT = 100

WORK_IN_PROGRESS_SUFFIX = '.wip'

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("top.html")


@app.route("/concatenated/<concatenated_id>", methods=["GET"])
def concatenated(concatenated_id):
    concatenated_filename = OUTPUT_DIR + '/' + concatenated_id
    if os.path.exists(concatenated_filename + WORK_IN_PROGRESS_SUFFIX):
        return "working... {}".format(metatag_for_redirect(concatenated_id))
    elif not os.path.exists(concatenated_filename):
        return "failed."
    return send_file(concatenated_filename, mimetype='image/jpeg')


@app.route("/upload", methods=["POST"])
def upload():
    if request.method != 'POST':
        return "request method not allowed."

    received_filenames = []
    for idx in range(1, ACCEPTABLE_IMAGE_COUNT):
        possible_received_file = IMAGE_NAME_PREFIX + '%02d' % idx
        if request.files.get(possible_received_file):
            received_file = request.files[possible_received_file]
            output_filename = INPUT_DIR + '/' + str(uuid.uuid4())
            received_file.save(output_filename)
            received_filenames.append(output_filename)

    if len(received_filenames) < 2:
        return "not enough images specified."

    concatenated_id = str(uuid.uuid4())
    t = threading.Thread(target=concat, args=(concatenated_id, received_filenames))
    t.start()

    return "uploaded... {}".format(metatag_for_redirect(concatenated_id))


def metatag_for_redirect(concatenated_id):
    url = "/concatenated/{}".format(concatenated_id)
    return "<meta http-equiv=\"refresh\" content=\"2;URL={}\">".format(url)


def concat(concatenated_id, received_filenames):
    concatenated_filename = OUTPUT_DIR + '/' + concatenated_id

    # touch
    open(concatenated_filename + WORK_IN_PROGRESS_SUFFIX, 'a').close()

    concat = concatss.ConcatScreenShot()
    concatenated_image = concat.concatenate_images(received_filenames, concatenated_filename)

    os.remove(concatenated_filename + WORK_IN_PROGRESS_SUFFIX)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
