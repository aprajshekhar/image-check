import subprocess

import sys


class DockerClient:
    def pull_image(self, name, tag_name='latest'):
        print "name %s" % name
        print "tag %s" % tag_name
        docker_pull = subprocess.Popen(['docker', 'pull', name+':'+tag_name], stderr=subprocess.PIPE)

        for line in docker_pull.stderr:
            print line
        docker_pull.wait()

        if docker_pull.returncode != 0:
            return False
        return True

    def remove(self, name):
        image_tags = name.split(":")
        print "removing %s" % image_tags[0]

        try:
            image_id = self._get_image_id(image_tags[0])
            docker_remove = subprocess.Popen(['docker', 'rmi', '--force', image_id], stderr=subprocess.PIPE)

            for line in docker_remove:
                print(line)
            docker_remove.wait()

            if docker_remove.returncode != 0:
                print('image '+image_tags[0]+' could not be removed')
        except Exception, e:
            print("Could not remove %s" % image_tags[0])
            print("reason %s" % e)
            sys.stdout.flush()
            sys.stderr.flush()

    def _get_image_id(self, image_name):
        image_id = subprocess.check_output(['docker', 'images', '-q', image_name])
        return image_id
