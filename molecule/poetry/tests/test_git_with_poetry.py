import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ["MOLECULE_INVENTORY_FILE"]
).get_hosts("all")


@pytest.mark.parametrize(
    "file_path",
    [
        "/var/local/test/app/wsgi.py",
        "/var/local/test/bin/setup_environment.sh",
        "/var/local/test/env.d/environment.conf",
        "/var/local/test/git",
        "/var/local/test/.poetry/bin/poetry",
        "/var/local/test/.cache/pypoetry",
        "/etc/systemd/system/test-webserver.service",
    ],
)
def test_file_path(host, file_path):
    """Check if role deployed files correctly"""
    assert host.file(file_path).exists


def test_user(host):
    """Check if role created correct user"""
    user = host.user("test")
    assert user.exists
    assert user.group == "test"
    assert user.home == "/var/local/test"


@pytest.mark.parametrize(
    "file,user",
    [
        ("/var/local/test/app/wsgi.py", "test"),
        ("/etc/systemd/system/test-webserver.service", "root"),
    ],
)
def test_file_owner(host, file, user):
    """Check if files have correct owner."""
    assert host.file(file).user == user


def test_running_services(host):
    """Check if systemd service is running correctly."""
    service = host.service("test-webserver")
    assert service.is_running
    assert service.is_enabled


# def test_service_uses_venv(host):
#     """Check if gunicorn process runs as expected."""
#     master = host.process.get(user="test_with_poetry", comm="gunicorn")
#     assert master is not None
#     assert (
#         "/var/local/test_without_setup/.poetry/bin -c gunicorn.conf.py wsgi.py"
#         in master.args
#     )
#     workers = host.process.filter(ppid=master.pid)
#     assert len(workers) == 4


def test_webserver_response(host):
    """Check if webserver returns correct response."""
    cmd = host.run("curl -v http://127.0.0.1:8000")
    assert cmd.succeeded
    assert "HTTP/1.1 200 OK" in cmd.stdout
