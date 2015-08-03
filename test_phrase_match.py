# -*- coding: utf-8 -*-
from fixtures import *


@pytest.fixture(scope="function", autouse=True)
def clear_solr(solr):
    solr.delete(q='*:*')


def test_phrase_match_exact(solr):
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


def test_phrase_match_ignores_lowercase(solr):
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


def test_phrase_match_ignores_uppercase(solr):
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


def test_phrase_match_ignores_punctuation(solr):
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


def test_phrase_match_trims_whitespace(solr):
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


def test_phrase_match_trims_inner_whitespace(solr):
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


def test_phrase_match_replaces_non_ascii_characters(solr):
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


def test_phrase_match_ignores_special_characters(solr):
    index = u'Colorless Green-Ideas Sleep=Furiously #?&[]()'
    query = u'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('phrase_match') for x in result][0]
