import subprocess


class ContainerAgent(object):

    def __init__(self):
        pass

    @classmethod
    def get_contaner_id(cls):
        bash_command = "cat /etc/hostname"
        process = subprocess.Popen(bash_command.split(), stdout=subprocess.PIPE)
        output, _ = process.communicate()
        cid = output.decode("utf-8").strip()
        return cid
