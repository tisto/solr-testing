# -*- coding: utf-8 -*-
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


def prepare_solrconfig():
    with open('templates/solrconfig.xml', 'r') as template:
        with open(
            'test-solr/solr/collection1/conf/solrconfig.xml',
            'w'
        ) as solrconfig:
            solrconfig.write(template.read())


def prepare_schema():
    with open('templates/phrase_match-schema.xml', 'r') as template:
        with open(
            'test-solr/solr/collection1/conf/schema.xml',
            'w'
        ) as schema:
            schema.write(template.read())


@pytest.fixture(scope="module", autouse=True)
def solr(request):
    prepare_solrconfig()
    prepare_schema()
    solr_process = subprocess.Popen(
        SOLR_START_CMD,
        stdout=subprocess.PIPE,
        shell=True,
        preexec_fn=os.setsid,
        cwd=TEST_DIR
    )

    def fin():
        print('Finalizing Solr')
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
            print('Solr Instance could not be started !!!')

    request.addfinalizer(fin)
    return solr_process


@pytest.fixture(scope="function", autouse=True)
def clear_solr(request):
    solr = pysolr.Solr(SOLR_URL)
    solr.delete(q='*:*')


def test_title():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'title': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'title:"Colorless Green Ideas Sleep Furiously"'
    )
    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('title') for x in result][0]


def test_phrase_match_exact():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_lowercase():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'phrase_match:"colorless green ideas sleep furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_uppercase():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'colorless green ideas sleep furiously',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'colorless green ideas sleep furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_punctuation():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'Colorless, Green; Ideas. Sleep? Furiously!',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless, Green; Ideas. Sleep? Furiously!' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_trims_whitespace():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': '  Colorless Green Ideas Sleep Furiously         ',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'  Colorless Green Ideas Sleep Furiously         ' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_trims_inner_whitespace():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'Colorless    Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless    Green Ideas Sleep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_special_characters():
    solr = pysolr.Solr(SOLR_URL)
    solr.add([{
        'id': '1',
        'phrase_match': 'Cölorless Grêen Idéaß Slèep Furiously #()[]$%',
    }])

    result = solr.search(
        'phrase_match:"c lorless gr en id a sl ep furiously"'
    )

    assert 1 == result.hits
    assert u'C\ufffd\ufffdlorless Gr\ufffd\ufffden Id\ufffd\ufffda\ufffd\ufffd Sl\ufffd\ufffdep Furiously #()[]$%' == \
        [x.get('phrase_match') for x in result][0]
