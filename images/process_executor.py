import subprocess


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
        docker_remove = subprocess.Popen(['docker', 'rmi', '--force',image_tags[0]], stderr=subprocess.PIPE)

        for line in docker_remove:
            print(line)
        docker_remove.wait()

        if docker_remove.returncode != 0:
            print('image '+image_tags[0]+' removed')
