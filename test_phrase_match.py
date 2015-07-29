import subprocess
import pysolr
import pytest
import time
import urllib2
import os
import signal
import sys


TEST_DIR = 'test-solr'
SOLR_URL = 'http://localhost:8989/solr'
SOLR_PING_URL = 'http://localhost:8989/solr/admin/ping'
SOLR_PORT = '8989'
SOLR_START_CMD = 'java -Djetty.port={} -jar start.jar'.format(SOLR_PORT)


@pytest.fixture(scope="module", autouse=True)
def solr(request):
    solr_process = subprocess.Popen(
        SOLR_START_CMD,
        stdout=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid,
        cwd=TEST_DIR
    )

    def fin():
        os.killpg(solr_process.pid, signal.SIGTERM)

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
            fin()
            sys.stdout.write('Solr Instance could not be started !!!')

    request.addfinalizer(fin)
    return solr_process


def test_title():
    solr = pysolr.Solr(SOLR_URL)
    solr.delete(q='*:*')

    solr.add([{
        'id': '1',
        'title': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'title:"Colorless Green Ideas Sleep Furiously"'
    )
    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('title') for x in result][0][0]
