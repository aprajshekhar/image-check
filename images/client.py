import traceback

__author__ = 'A.P. Rajshekhar'

import docker
import json
import docker.errors as errors


class Client:
    def __init__(self):
        self.docker_client = docker.Client(base_url='unix://var/run/docker.sock', timeout=120)

    def pull_image(self, name, tag_name='latest'):
        """
        pull an image based on the name and the tag name. If the image exists, print the
        data being pulled, else reurn false
        :param name: name of the image
        :param tag_name: name of the tag
        :return: True if the image can be pulled, false if it cannot be
        """
        try:
            response = self.docker_client.pull(name, tag=tag_name, stream=True)
            return self._check_response(response)
        except errors.APIError, errors:
            return False
        except Exception:
            return False


    def _check_response(self, response):
        image_exist = True
        # the response contains multiple json docs. Hence,
        # parsing the response line by line
        for line in response:
            print "response: %s" % line

            if self._is_status_ok(line) is False:
                image_exist = False
                break

        return image_exist

    def _is_status_ok(self, response_line):
        # print response_line
        data = json.loads(response_line)
        status = data.get('status')
        print "status of pull %s" % status
        error_detail = data.get('errorDetail')
        print "error detail if present %s" % error_detail
        if status is not None and 'not found' in data.get('status'):
            return False
        elif error_detail is not None:
            return False
        else:
            return True

    def remove(self, name):
        """
        Remove the image and associated container for the specified image name
        :param name: name of the image to be removed
        :return: response
        """

        print "removing %s" % name
        try:
            self._remove_container(name)
            self.docker_client.remove_image(name, force=True)
        except errors.APIError:
            print "Could not remove %s" % name
        except Exception, e:
            print "Could not remove image due to exception %s" % e.message

    def _remove_container(self, image_name):
        ids = self.docker_client.images(name=image_name, quiet=True)
        print "ids %s" % ids
        for image_id in ids:
            try:
                self.docker_client.remove_container(image_id, force=True)
            except errors.APIError, e:
                print "Could not remove %s" % image_id
                print "Error is %s" % e.response
            except Exception, e:
                print "Could not remove container due to exception %s" % e.message