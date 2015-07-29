import subprocess
import pytest
import time
import urllib2
import os
import signal
import sys


TEST_DIR = 'test'
SOLR_URL = 'http://localhost:8989/solr'
SOLR_PING_URL = 'http://localhost:8989/solr/admin/ping'
SOLR_PORT = '8989'


@pytest.fixture(scope="module", autouse=True)
def solr(request):
    solr_process = subprocess.Popen(
        'java -Djetty.port={} -jar start.jar'.format(SOLR_PORT),
        stdout=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid,
        cwd=TEST_DIR
    )
    # Poll Solr until it is up and running
    for i in range(1, 10):
        try:
            result = urllib2.urlopen(SOLR_PING_URL)
            if result.code == 200:
                if '<str name="status">OK</str>' in result.read():
                    break
        except urllib2.URLError:
            time.sleep(3)
            sys.stdout.write('.')
        if i == 9:
            subprocess.call(
                './solr-instance stop',
                shell=True,
                close_fds=True,
                cwd=TEST_DIR
            )
            sys.stdout.write('Solr Instance could not be started !!!')

    def fin():
        os.killpg(solr_process.pid, signal.SIGTERM)

    request.addfinalizer(fin)
    return solr_process


def func(x):
    return x + 1


def test_answer():
    assert func(4) == 5
