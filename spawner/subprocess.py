import os
import shutil
import tempfile
import time
from threading import Thread, Event

import tornado.process
from tornado.ioloop import IOLoop


def start_process(args, directory, io_loop=None):
    cmd = ("cd %s;" % directory +
           " ".join(args) +
           " > log.out 2> log.err & " +
           "echo $! > pid && " +
           "echo start > status && "
           "wait $(cat pid)")
    return tornado.process.Subprocess(cmd, shell=True, io_loop=io_loop)


def do_nothing():
    pass


class Job(object):
    """ A single user defined job """
    def __init__(self, spawner, args, directory=None, on_start=do_nothing,
            on_finish=do_nothing):
        self.spawner = spawner
        self.args = args
        self.on_start = on_start
        self.on_finish = on_finish
        self.directory = directory or tempfile.mkdtemp(prefix='spawner-')
        self.process = start_process(self.args, self.directory, self.io_loop)

        while not os.path.exists(os.path.join(self.directory, 'pid')):
            time.sleep(0.01)
        on_start()  # we choose to block until start for processes
        with open(os.path.join(self.directory, 'pid')) as f:
            self.id = int(f.read())

        self.done_event = Event()
        self.status = 'running'

        def done_status():
            self.status = 'finished'

        self.process.set_exit_callback(lambda _: [on_finish(),
                                                  done_status(),
                                                  self.done_event.set()])

    def kill(self):
        try:
            self.process.proc.kill()
        except OSError:
            pass
        self.spawner.jobs.remove(self)

    def get_stdout(self):
        """ Returns an iterator of lines of stdout, can be called repeatedly """
        with open(os.path.join(self.directory, 'log.out')) as f:
            for line in f:
                yield line.rstrip()

    def get_stderr(self):
        """ Returns an iterator of lines of stderr, can be called repeatedly """
        with open(os.path.join(self.directory, 'log.err')) as f:
            for line in f:
                yield line.rstrip()

    @property
    def io_loop(self):
        return self.spawner.io_loop

    def join(self):
        self.done_event.wait()

    def __del__(self):
        try:
            shutil.rmtree(self.directory)
        except (IOError, OSError):
            pass


class LocalProcessSpawner(object):
    """ Context to create and manage local jobs

    Examples
    --------
    >>> spawner = LocalProcessSpawner()

    >>> job = spawner.spawn(['echo', 'hello, world!'])
    >>> job.join()
    >>> list(job.get_stdout())
    ['hello, world!']

    Optionally provide callbacks for start and finish

    >>> log = []
    >>> job = spawner.spawn(['echo', 'hello, world!'],
    ...                     on_start=lambda: log.append('started'),
    ...                     on_finish=lambda: log.append('finished'))
    >>> job.join()
    >>> log
    ['started', 'finished']
    """
    Job = Job
    def __init__(self, io_loop=None, directory=None):
        self.jobs = set()
        self.io_loop = io_loop or IOLoop()
        if not self.io_loop._running:
            self._io_loop_thread = Thread(target=self.io_loop.start)
            self._io_loop_thread.daemon = True
            self._io_loop_thread.start()
        while not self.io_loop._running:
            sleep(0.001)

    def spawn(self, args, on_start=do_nothing, on_finish=do_nothing):
        """ Spawn new job

        Parameters
        ----------
        args: list
            List of terms for command, like ``['sleep', '10']``
        on_start: callable
            Function to run when job starts
        on_finish: callable
            Function to run when job finishes
        """
        job = Job(self, args, on_start=on_start, on_finish=on_finish)
        self.jobs.add(job)
        return job

    def close(self):
        """ Close all active jobs """
        for job in list(self.jobs):
            job.kill()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
