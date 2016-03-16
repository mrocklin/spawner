from spawner import LocalProcessSpawner
import pytest


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
