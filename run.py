__author__ = 'A.P. Rajshekhar'

import validate_images
import argparse


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
    check_image.start_check(parse_arg())

