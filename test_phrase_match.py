# -*- coding: utf-8 -*-
from fixtures import *

import pysolr

SOLR_URL = 'http://localhost:8989/solr/phrase_match'


@pytest.fixture(scope="function", autouse=True)
def clear_solr(request):
    solr = pysolr.Solr(SOLR_URL)
    solr.delete(q='*:*')


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
