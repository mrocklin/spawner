class Job(object):
    def __init__(self, spawner, process):
        self.spawner = spawner
        self.process = process

    def kill(self):
        raise NotImplementedError()

    @property
    def stdout(self):
        raise NotImplementedError()

    @property
    def stderr(self):
        raise NotImplementedError()

    def id(self):
        raise NotImplementedError()

    @property
    def status(self):
        raise NotImplementedError()


class Spawner(object):
    Job = Job
    def __init__(self):
        self.jobs = set()

    def spawn(self, args):
        proc = self._spawn(args)
        job = self.Job(self, proc)
        self.jobs.add(job)
        return job

    def _spawn(self, args):
        raise NotImplementedError()

    def close(self):
        for job in list(self.jobs):
            job.kill()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
