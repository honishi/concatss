#!/usr/bin/env python
# encoding=utf-8

import os
from PIL import Image
import cProfile

MINIMUM_REQUIRED_MATCHED_HEIGHT = 50

# scan interval is used for performance improvement
SCAN_INTERVAL_Y = 5
SCAN_INTERVAL_X = 25

STATUS_LOG_SUFFIX = '.status'


# public methods
def concatenate_images(input_filenames, output_filename, log_status=False):
    """
    returns True if files are successfully concatenated
    """
    if len(input_filenames) < 2:
        return False

    status_log_filename = None
    if log_status:
        status_log_filename = output_filename + STATUS_LOG_SUFFIX
        open(status_log_filename, 'w').close()  # touch

    upper_image_filename = input_filenames[0]
    input_filenames.remove(upper_image_filename)
    upper_image = Image.open(upper_image_filename, 'r')

    processed_count = 1
    concatenated_image = None
    for lower_image_filename in input_filenames:
        lower_image = Image.open(lower_image_filename, 'r')
        log_header = "processing {} of {}: ".format(processed_count, len(input_filenames))

        concatenated_image = _concatenate(
            upper_image, lower_image, status_log_filename, log_header)

        if concatenated_image is None:
            break
        upper_image = concatenated_image

        processed_count += 1

    if concatenated_image:
        concatenated_image.save(output_filename, 'PNG')

    if log_status:
        os.remove(status_log_filename)

    return True


# internal methods
def _concatenate(upper_image, lower_image, status_log_filename=None, log_header=""):
    print("upper image size: {}, {}".format(upper_image.size[0], upper_image.size[1]))
    print("lower image size: {}, {}".format(lower_image.size[0], lower_image.size[1]))

    if upper_image.size[0] != lower_image.size[0]:
        return None

    # use upper image width as common image width
    image_width = upper_image.size[0]

    # for performance, use getdata() instead of getpixel()
    upper_pixels = list(upper_image.getdata())
    lower_pixels = list(lower_image.getdata())

    upper_image_scan_start_offset = upper_image.size[1] - MINIMUM_REQUIRED_MATCHED_HEIGHT
    upper_image_scan_end_offset = upper_image.size[1] - lower_image.size[1]//2
    print("scan start offset: {}, end offset: {}".format(
          upper_image_scan_start_offset, upper_image_scan_end_offset))

    lower_image_scan_end_offset = lower_image.size[1] - MINIMUM_REQUIRED_MATCHED_HEIGHT

    offset_candidates = []
    current_lowest_difference = None

    for upper_offset in range(upper_image_scan_start_offset, upper_image_scan_end_offset, -1):
        # print("scanning upper image, offset: {}".format(upper_offset))
        if status_log_filename:
            f = open(status_log_filename, 'w')  # overwrite
            f.write("{}scanning images, offset {}\n".format(log_header, upper_offset))
            f.close()

        for lower_offset in range(0, lower_image_scan_end_offset):
            # print("scanning lower image, offset: {}".format(lower_offset))
            if upper_offset <= lower_offset:
                continue

            difference = _scan_images(image_width, upper_pixels, upper_offset, lower_pixels,
                                      lower_offset, current_lowest_difference)
            offset_candidates.append((upper_offset, lower_offset, difference))

            if current_lowest_difference is None:
                current_lowest_difference = difference
            else:
                if difference < current_lowest_difference:
                    current_lowest_difference = difference

            # print("upper offset: {0:4d}, lower offset: {1:4d}, diff: {2:5d}, lowest: {3:5d}"
            #       .format(upper_offset, lower_offset, difference, current_lowest_difference))

    chosen_candidate = _choose_offset_candidate(offset_candidates)
    chosen_upper_offset = chosen_candidate[0]
    chosen_lower_offset = chosen_candidate[1]
    print("concatenate using offset, upper: {}, lower: {}"
          .format(chosen_upper_offset, chosen_lower_offset))

    return _merge(upper_image, chosen_upper_offset, lower_image, chosen_lower_offset)


def _choose_offset_candidate(candidates):
    sorted_candidates = sorted(candidates, key=lambda x:x[2])   # order by diff asc
    """
    idx = 0
    for candidate in sorted_candidates:
        print("candidate: {} {}".format(idx, candidate))
        if 20 < idx:
            break
        idx += 1
    """

    return sorted_candidates[0]

def _scan_images(image_width, upper_pixels, upper_offset, lower_pixels, lower_offset,
                 stop_difference):
    """
    returns difference between images between images
    """
    difference = 0
    detected_too_different = False

    for y in range(0, MINIMUM_REQUIRED_MATCHED_HEIGHT, SCAN_INTERVAL_Y):
        for x in range(0, image_width-1, SCAN_INTERVAL_X):
            # pixel scan section
            p = image_width * upper_offset
            p += y * image_width + x
            if not p < len(upper_pixels):
                # scanned every possible pixels
                return difference
            upper_pixel = upper_pixels[p]

            p = image_width * lower_offset
            p += y * image_width + x
            if not p < len(lower_pixels):
                return difference
            lower_pixel = lower_pixels[p]

            difference += _calculate_pixel_difference(upper_pixel, lower_pixel)

            if stop_difference is not None and stop_difference < difference:
                detected_too_different = True
                break
        if detected_too_different:
            break

    return difference


def _calculate_pixel_difference(a, b):
    difference = _delta(a[0], b[0])     # red
    difference += _delta(a[1], b[1])    # green
    difference += _delta(a[2], b[2])    # blue

    return difference


def _delta(a, b):
    if a < b:
        return b - a
    else:
        return a - b


def _merge(upper_image, upper_offset, lower_image, lower_offset):
    cropped_upper_image = upper_image.crop(
        (0, 0, upper_image.size[0], upper_offset))
    # print("{}, {}".format(lower_image.size[1], lower_offset))
    cropped_lower_image = lower_image.crop(
        (0, lower_offset, lower_image.size[0], lower_image.size[1]))

    print("cropped upper size: {}, {}".format(
          cropped_upper_image.size[0], cropped_upper_image.size[1]))
    print("cropped lower size: {}, {}".format(
          cropped_lower_image.size[0], cropped_lower_image.size[1]))

    merged_image = Image.new(
        'RGB',
        (cropped_upper_image.size[0], cropped_upper_image.size[1] + cropped_lower_image.size[1]),
        (255, 255, 255))
    merged_image.paste(cropped_upper_image, (0, 0))
    merged_image.paste(cropped_lower_image, (0, cropped_upper_image.size[1]))

    # test: merged_image.save('./merged.png', 'PNG')
    return merged_image


if __name__ == "__main__":
    if 1:
        concatenate_images(
            ["./sample/input1.png", "./sample/input2.png", "./sample/input3.png"],
            # ["./sample/input1.png", "./sample/input2.png"],
            # ["./sample/input2.png", "./sample/input3.png"],
            "./sample/output.png")
    else:
        cProfile.run(
            'concatenate_images('
            '["./sample/input1.png", "./sample/input2.png", "./sample/input3.png"],'
            # '["./sample/input1.png", "./sample/input2.png"],'
            '"./sample/output.png")')
