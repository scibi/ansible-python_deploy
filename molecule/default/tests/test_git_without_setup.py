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
        "/var/local/test/env.d/virtualenv.conf",
        "/var/local/test/git",
        "/var/local/test/venv",
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


def test_webserver_response(host):
    """Check if webserver returns correct response."""
    cmd = host.run("curl http://127.0.0.1:8000 --verbose")
    assert cmd.succeeded
    assert "OK" == cmd.stdout
