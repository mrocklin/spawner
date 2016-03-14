
import pytest
from spawner import SSH


def test_subprocess():
    with SSH() as s:
        a = s.spawn(['echo', 'hello'])
        b = s.spawn(['echo', 'world'])
        assert a.id != b.id
        assert a.status in ('running', 'finished')

        assert a.stdout.read() == b"hello\n"
        assert b.stdout.read() == b"world\n"


@pytest.mark.xfail(reason="pids stick around longer than expected")
def test_cleanup():
    with SubProcess() as s:
        a = s.spawn(['sleep', '100'])

    assert a.status is 'finished'
