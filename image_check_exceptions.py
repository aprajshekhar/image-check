__author__ = 'randalap'


class ImageCheckException(Exception):
    def __init__(self, message):
        super(ImageCheckException, self).__init__(message)
        self.message = message
