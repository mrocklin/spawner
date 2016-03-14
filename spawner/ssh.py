import paramiko
import uuid

from . import core

class Job(core.Job):
    def __init__(self, spawner, client, args, id):
        self.client = client
        self.args = args
        self.id = id = str(uuid.uuid1())
        cmd = ' '.join(args) + ' > %s.out 2>&1 & echo $!' % s
        self._stdin, self._stdout, self._stderr = self.client.exec_command(cmd)
        self.pid = int(next(self.stdout).split(' ')[1])

    @property
    def status(self):
        try:

            os.kill(self.process.pid, 0)  # http://stackoverflow.com/a/568285/616616
        except OSError:
            return 'finished'
        else:
            return 'running'


class SSH(core.Spawner):
    Job = Job

    def __init__(self, hosts):
        core.Spawner.__init__(self)

        self.hosts = hosts
        self.jobs = {host: [] for host in hosts}

    def spawn(self, args):
        host = self.get_host()
        client = paramiko.SSHClient()
        client.connect(host)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return Job(self, client, args)

    def get_host(self):
        return random.choice(list(self.hosts))
