from spawner import SubProcess
import pytest


def test_subprocess():
    s = SubProcess()
    a = s.spawn(['echo', 'hello'])
    b = s.spawn(['echo', 'world'])
    assert a.id != b.id
    assert a.status in ('running', 'finished')

    assert a.stdout.read() == b"hello\n"
    assert b.stdout.read() == b"world\n"

    a.kill()
    b.kill()


@pytest.mark.xfail(reason="pids stick around longer than expected")
def test_cleanup():
    with SubProcess() as s:
        a = s.spawn(['sleep', '100'])

    assert a.status is 'finished'
