import sys
import yaml
import Queue
import os
import time
import file_utils
import image_check_exceptions
import images.process_executor as docker_client
import images.search as search
from images import search_images

__author__ = 'A.P. Rajshekhar'


class SearchAndValidate:
    """
    Issues a search for ISV images and validates them using docker pull
    """
    CONFIG_FILE_PATH = '/etc/config.yaml'
    CONFIG_ENV_NAME = 'CONFIG_FILE_PATH'

    def __init__(self):
        self.queue = Queue.Queue()
        self.docker_client = docker_client.DockerClient()
        config_path = os.environ.get(SearchAndValidate.CONFIG_ENV_NAME) or SearchAndValidate.CONFIG_FILE_PATH
        self.config = yaml.safe_load(open(config_path))
        self.pulled_images = []
        self.failed_images = []
        file_utils.delete_file()

    def __process_image_queue(self):
        # result_queue = Queue.Queue()

        print('in process image')
        for image in list(self.queue.queue):
            image_tag = image.split(':')
            image_name = image_tag[0]
            if 'add_host' in self.config and self.config['add_host'] == 'true':
                image_name = self.host + image_name
            tag = image_tag[1] if len(image_tag) > 1 else 'latest'
            result = self.docker_client.pull_image(image_name, tag)

            if result is False:
                self.failed_images.append(image_name)
                # print "result list is %s" % self.failed_images
            else:
                self.pulled_images.append(image_name)
                # print "result list for pulled images is %s" % self.pulled_images

            print "Waiting for 30 sec before next pull"
            sys.stderr.flush()
            sys.stdout.flush()
            time.sleep(30)

    def start_check(self, environment='ci'):
        """
        Starts the process of ISV image validation. It first issues a search
        and tries to pull the images whose names are returned by the search

        :param environment: environment against which search has to be executed
        :return:
        """
        self.host = self.config[environment]['host']
        query_param = self.config['param']
        search_type = self.config['search_type']

        search_client = search_images.SearchImages if search_type == 'ImageRepository' else search.StrataSearch(self.host+"rs/search")
        search_client.rows = 200
        results = list(search_client.search(query_param))
        results_paginated = [results[i:i+5] for i in range(0, len(results), 4)]

        print "paginated results %s" % results_paginated
        sys.stderr.flush()
        sys.stdout.flush()

        for lists in results_paginated:
            for result in lists:
                self.queue.put(result)
                self.__process_image_queue()
                # print "failed images list in start_check %s" % self.failed_images
                # print "pulled images list in start_check is %s" % self.pulled_images
                self._remove_images()

        self._save_result()

        print "length of unsuccessful pull %s" % len(self.failed_images)
        sys.stderr.flush()
        sys.stdout.flush()
        if len(self.failed_images) > 0:
            message = '%s the images could not be pulled' % self.failed_images
            print message
            raise image_check_exceptions.ImageCheckException(message)

    def _remove_images(self):
        for image in list(self.queue.queue):
            self.docker_client.remove(image)
        self.queue.queue.clear()
            # print "Waiting for 30 seconds before removing next pulled image"

    def _save_result(self):
        file_utils.delete_file()
        with open('./results.txt', mode='w') as out_file:
            if len(self.failed_images) > 0:
                print >>out_file, 'Following images could not be pulled'
                print >>out_file, '\n'.join(self.failed_images)
            if len(self.pulled_images) > 0:
                print >>out_file, '\nFollowing images have been pulled'
                print >>out_file, '\n'.join(self.pulled_images)