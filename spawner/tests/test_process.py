from spawner import Process
from time import time

def test_process():
    p = Process(['echo', 'hello'])
    p.start()
    assert isinstance(p.pid, int)
    p.join()
    assert list(p.get_stdout()) == ['hello']
    assert list(p.get_stdout()) == ['hello']


def test_join():
    p = Process(['sleep', '0.5'])
    p.start()
    start = time()
    p.join()
    end = time()
    assert end - start >= 0.5
