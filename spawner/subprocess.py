import os
import tempfile
from threading import Thread, Event

import tornado.process
from tornado.ioloop import IOLoop


def start_process(args, directory, io_loop=None):
    cmd = ("cd %s;" % directory +
           " ".join(args) +
           " > log.out 2> log.err & " +
           "echo $! > pid && " +
           "echo start > status")
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
        on_start()  # we start immediately, no waiting involved
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
        with open(os.path.join(self.directory, 'log.out')) as f:
            for line in f:
                yield line.rstrip()

    def get_stderr(self):
        with open(os.path.join(self.directory, 'log.err')) as f:
            for line in f:
                yield line.rstrip()

    def id(self):
        return self.process.pid

    @property
    def io_loop(self):
        return self.spawner.io_loop

    def join(self):
        self.done_event.wait()


class LocalProcessSpawner(object):
    """ Context to create and manage local jobs """
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
        job = Job(self, args, on_start=on_start, on_finish=on_finish)
        self.jobs.add(job)
        return job

    def close(self):
        for job in list(self.jobs):
            job.kill()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
