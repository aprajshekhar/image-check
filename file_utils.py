import os

__author__ = 'A.P. Rajshekhar'


def delete_file():
    if os.path.exists('./results.txt'):
        os.remove('./results.txt')


def write(message):
    with open('./results.txt', mode='w') as out_file:
        print >>out_file, message