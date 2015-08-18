__author__ = 'A.P. Rajshekhar'

import images.client as client
import images.search as search
import yaml
import argparse
import Queue
import os


class SearchAndValidate:
    """
    Issues a search for ISV images and validates them using docker pull
    """
    CONFIG_FILE_PATH = '/etc/config.yaml'
    CONFIG_ENV_NAME = 'CONFIG_FILE_PATH'

    def __init__(self):
        self.queue = Queue.Queue()
        self.docker_client = client.Client()
        config_path = os.environ.get(SearchAndValidate.CONFIG_ENV_NAME) or SearchAndValidate.CONFIG_FILE_PATH
        self.config = yaml.safe_load(open(config_path))

    def __process_image_queue(self):
        # result_queue = Queue.Queue()
        result_list = []
        for image in list(self.queue.queue):
            image_tag = image.split(':')
            image_name = image_tag[0]
            tag = image_tag[1] if len(image_tag) > 1 else 'latest'
            result = self.docker_client.pull_image(image_name, tag)
            # result_queue.put({image: result})
            if result is False:
                # result_dict[image] = 'Image is not valid'
                result_list.append(image)

        return result_list

    def start_check(self, environment='ci'):
        """
        Starts the process of ISV image validation. It first issues a search
        and tries to pull the images whose names are returned by the search

        :param environment: environment against which search has to be executed
        :return:
        """
        host = self.config[environment]['host']
        query_param = self.config['param']

        search_client = search.StrataSearch(host+"rs/search")
        results = search_client.search(query_param)
        for result in results:
            print result
            self.queue.put(result)

        result = self.__process_image_queue()
        self._remove_images()
        self._save_result(result)
        if len(result) > 0:
            raise Exception('All the images could not be pulled')

    def _remove_images(self):
        for image in list(self.queue.queue):
            self.docker_client.remove(image)

    def _save_result(self, result):
        print result
        if os.path.exists('./results.txt'):
            os.remove('./results.txt')

        with open('./results.txt', mode='w') as out_file:
            print >>out_file, 'Following images could not be pulled'
            print >>out_file, '\n'.join(result)


def parse_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", help="the environment against which to run search")
    args = parser.parse_args()
    if args.env:
        return args.env
    else:
        return 'ci'

if __name__ == '__main__':
    check_image = SearchAndValidate()
    check_image.start_check(parse_arg())
