import image_check_exceptions

__author__ = 'A.P. Rajshekhar'

import validate_images
import argparse
from image_check_exceptions import ImageCheckException
import file_utils

def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", help="the environment against which to run search")
    args = parser.parse_args()
    if args.env:
        return args.env
    else:
        return 'ci'

if __name__ == '__main__':
    check_image = validate_images.SearchAndValidate()
    try:
        check_image.start_check(parse_arg())
    except ImageCheckException, e:
        raise
    except Exception, e:
        print e
        file_utils.delete_file()
        file_utils.write("Build has thrown exception not related to pull of image. Please check.")

