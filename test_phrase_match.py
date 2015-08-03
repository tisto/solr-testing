# -*- coding: utf-8 -*-
from fixtures import *

import pysolr

SOLR_URL = 'http://localhost:8989/solr/phrase_match'
SOLR_TIMEOUT = 1


@pytest.fixture(scope="function", autouse=True)
def clear_solr(request):
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
    solr.delete(q='*:*')


def test_phrase_match_exact():
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
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


def test_phrase_match_replaces_non_ascii_characters():
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
    solr.add([{
        'id': '1',
        'phrase_match': u'Cölorless Grêen Idéaß Slèep Furiously',
    }])

    result = solr.search(
        'phrase_match:"Colorless Green Ideass Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Cölorless Grêen Idéaß Slèep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_special_characters():
    index = u'Colorless Green-Ideas Sleep=Furiously #?&[]()'
    query = u'Colorless Green Ideas Sleep Furiously'
    solr = pysolr.Solr(SOLR_URL, timeout=SOLR_TIMEOUT)
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('phrase_match') for x in result][0]
