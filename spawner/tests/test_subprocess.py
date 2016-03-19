from spawner import LocalProcessSpawner
import pytest

from time import sleep


def test_LocalProcessSpawner():
    s = LocalProcessSpawner()

    a_flag = []
    def a_on_start():
        a_flag.append('start')
    def a_on_finish():
        a_flag.append('finish')

    a = s.spawn(['echo', 'hello'], on_start=a_on_start, on_finish=a_on_finish)

    b_flag = []
    def b_on_start():
        b_flag.append('start')
    def b_on_finish():
        b_flag.append('finish')

    b = s.spawn(['echo', 'world'], on_start=b_on_start, on_finish=b_on_finish)

    assert a.id != b.id

    a.join()
    b.join()

    assert next(a.get_stdout()) == "hello"
    assert next(b.get_stdout()) == "world"
    assert list(a.get_stderr()) == []
    assert list(b.get_stderr()) == []

    assert a_flag == ['start', 'finish']
    assert b_flag == ['start', 'finish']

    a.kill()
    b.kill()


def test_finish_correct_time():
    s = LocalProcessSpawner()

    L = []
    def append():
        L.append(None)

    job = s.spawn(['sleep', '1'], on_start=append, on_finish=append)
    sleep(0.5)
    assert len(L) == 1
    assert job.status != 'finished'
    for i in range(10):
        sleep(0.1)
    assert job.status == 'finished'
    assert len(L) == 2
