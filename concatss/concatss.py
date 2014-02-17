#!/usr/bin/env python
# encoding=utf-8

from PIL import Image
import cProfile

SCAN_RANGE = 50
# scan interval is used for performance improvement
#SCAN_INTERVAL_Y = 2
#SCAN_INTERVAL_X = 10
#SAME_PIXEL_ALLOWANCE = 32
## SAME_PIXEL_ALLOWANCE = 128

SCAN_INTERVAL_Y = 5
SCAN_INTERVAL_X = 25
SAME_PIXEL_ALLOWANCE = 32


class ConcatScreenShot(object):
# object life cycle
    def __init__(self):
        pass

# public methods
    def concatenate_images(self, input_filenames, output_filename):
        upper_image_filename = input_filenames[0]
        input_filenames.remove(upper_image_filename)
        upper_image = Image.open(upper_image_filename, 'r')

        for lower_image_filename in input_filenames:
            lower_image = Image.open(lower_image_filename, 'r')
            concatenated_image = self.scan_images(upper_image, lower_image)

            if concatenated_image is None:
                return False
            upper_image = concatenated_image

        concatenated_image.save(output_filename, 'PNG')
        return True

# internal methods
    def scan_images(self, upper_image, lower_image):
        print("upper image size: {}, {}".format(upper_image.size[0], upper_image.size[1]))
        print("lower image size: {}, {}".format(lower_image.size[0], lower_image.size[1]))

        if upper_image.size[0] != lower_image.size[0]:
            return None
        # use upper image width as common image width
        image_width = upper_image.size[0]

        # for performance, use getdata() instead of getpixel()
        upper_pixels = list(upper_image.getdata())
        lower_pixels = list(lower_image.getdata())

        upper_image_concat_height = 0
        lower_image_concat_height = 0
        found_concat_positions = False

        for upper_image_concat_height in range(
                upper_image.size[1] - SCAN_RANGE-1,
                upper_image.size[1] - SCAN_RANGE-1 - lower_image.size[1]//2,
                -1):
            # print("*** scanning upper height: {}".format(upper_image_concat_height))
            for lower_image_concat_height in range(
                    0,
                    lower_image.size[1]//2):
                # print("scanning lower height: {}".format(lower_image_concat_height))

                # pixel scan section
                found_concat_positions = True
                for y in range(0, SCAN_RANGE-1, SCAN_INTERVAL_Y):
                    for x in range(0, image_width-1, SCAN_INTERVAL_X):
                        # any functions *should* be manually inline expanded.
                        # cause the code here is a hot spot of this code.
                        p = image_width * upper_image_concat_height
                        p += y * image_width + x
                        upper_pixel = upper_pixels[p]

                        p = image_width * lower_image_concat_height
                        p += y * image_width + x
                        lower_pixel = lower_pixels[p]

                        diff_red = upper_pixel[0] - lower_pixel[0]
                        if diff_red < 0:
                            diff_red *= -1
                        if SAME_PIXEL_ALLOWANCE < diff_red:
                            found_concat_positions = False
                            break

                        diff_green = upper_pixel[1] - lower_pixel[1]
                        if diff_green < 0:
                            diff_green *= -1
                        if SAME_PIXEL_ALLOWANCE < diff_green:
                            found_concat_positions = False
                            break

                        diff_blue = upper_pixel[2] - lower_pixel[2]
                        if diff_blue < 0:
                            diff_blue *= -1
                        if SAME_PIXEL_ALLOWANCE < diff_blue:
                            found_concat_positions = False
                            break
                    if found_concat_positions is False:
                        break
                if found_concat_positions is True:
                    break
            if found_concat_positions is True:
                break

        print("found position: {} upper concat: {}, lower concat: {}".format(
              "yes" if found_concat_positions is True else "no",
              upper_image_concat_height, lower_image_concat_height))

        if found_concat_positions is False:
            return None

        return self.merge_images(upper_image, upper_image_concat_height,
                                 lower_image, lower_image_concat_height)

    def merge_images(self, upper_image, upper_image_concat_height,
                     lower_image, lower_image_concat_height):
        cropped_upper_image = upper_image.crop(
            (0, 0, upper_image.size[0], upper_image_concat_height))
        print("{}, {}".format(lower_image.size[1], lower_image_concat_height))
        cropped_lower_image = lower_image.crop(
            (0, lower_image_concat_height, lower_image.size[0], lower_image.size[1]))

        print("cropped upper size: {}, {}".format(
              cropped_upper_image.size[0], cropped_upper_image.size[1]))
        print("cropped lower size: {}, {}".format(
              cropped_lower_image.size[0], cropped_lower_image.size[1]))

        merged_image = Image.new(
            'RGB',
            (cropped_upper_image.size[0],
             cropped_upper_image.size[1] + cropped_lower_image.size[1]),
            (255, 255, 255))
        merged_image.paste(cropped_upper_image, (0, 0))
        merged_image.paste(cropped_lower_image, (0, cropped_upper_image.size[1]))

        # test
        # merged_image.save('./merged.png', 'PNG')

        return merged_image


if __name__ == "__main__":
    cProfile.run('concatss = ConcatScreenShot()')
    cProfile.run(
        'concatss.concatenate_images('
        '["./sample/input1.png", "./sample/input2.png", "./sample/input3.png"],'
        # '["./sample/input1.png", "./sample/input2.png"],'
        '"./sample/output.png")')
