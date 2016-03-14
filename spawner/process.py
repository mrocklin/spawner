import tempfile
from time import sleep
import subprocess
import os

class Process(object):
    def __init__(self, args, directory=None):
        self.directory = directory or tempfile.mkdtemp(prefix='spawner-')
        self.args = args
        self.process = None

    def start(self):
        cmd = ("cd %s; " % self.directory +
               " ".join(self.args) +
               " > log.out 2> log.err & "
               "echo $! > pid && " +
               "echo start > status")
        self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True)

        while not os.path.exists(os.path.join(self.directory, 'pid')):
            sleep(0.01)

    @property
    def pid(self):
        with open(os.path.join(self.directory, 'pid')) as f:
            return int(f.read())

    def get_stdout(self):
        with open(os.path.join(self.directory, 'log.out')) as f:
            for line in f:
                yield line.rstrip()

    def get_stderr(self):
        with open(os.path.join(self.directory, 'log.err')) as f:
            for line in f:
                yield line.rstrip()

    def join(self):
        pid = self.pid
        while True:
            try:
                os.kill(pid, 0)
                sleep(0.1)
            except ProcessLookupError:
                break
