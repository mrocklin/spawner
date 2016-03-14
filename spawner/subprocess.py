import subprocess
import os

from . import core

class Job(core.Job):
    def __init__(self, spawner, process):
        self.spawner = spawner
        self.process = process

    def kill(self):
        self.process.kill()
        self.spawner.jobs.remove(self)

    @property
    def stdout(self):
        return self.process.stdout

    @property
    def stderr(self):
        return self.process.stderr

    def id(self):
        return self.process.pid

    @property
    def status(self):
        try:
            os.kill(self.process.pid, 0)  # http://stackoverflow.com/a/568285/616616
        except OSError:
            return 'finished'
        else:
            return 'running'


class SubProcess(core.Spawner):
    Job = Job
    def _spawn(self, args):
        return subprocess.Popen(args, stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
