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
    index = 'Colorless Green Ideas Sleep Furiously'
    query = 'colorless green ideas sleep furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_uppercase(solr):
    index = 'colorless green ideas sleep furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'colorless green ideas sleep furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_punctuation(solr):
    index = 'Colorless, Green; Ideas. Sleep? Furiously!'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless, Green; Ideas. Sleep? Furiously!' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_trims_whitespace(solr):
    index = '  Colorless Green Ideas Sleep Furiously         '
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'  Colorless Green Ideas Sleep Furiously         ' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_trims_inner_whitespace(solr):
    index = 'Colorless    Green Ideas Sleep Furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless    Green Ideas Sleep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_replaces_non_ascii_characters(solr):
    index = u'Cölorless Grêen Idéaß Slèep Furiously'
    query = u'Colorless Green Ideass Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Cölorless Grêen Idéaß Slèep Furiously' == \
        [x.get('phrase_match') for x in result][0]


def test_phrase_match_ignores_special_characters(solr):
    index = u'Colorless Green-Ideas Sleep=Furiously #?/[]()'
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


def test_phrase_match_ignores_content_in_brackets(solr):
    index = u'Colorless Green Ideas Sleep Furiously (or not)'
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


def test_phrase_match_ignores_everything_after_a_colon(solr):
    index = u'Colorless Green Ideas Sleep Furiously: or not'
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


def test_phrase_match_replaces_ampersands_with_and(solr):
    index = u'Colorless & Green Ideas Sleep Furiously'
    query = u'Colorless and Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('phrase_match') for x in result][0]


@pytest.mark.parametrize("index, query", [
    (
        'Revista latino-americana de enfermagem',
        'Revista Latino-Americana de Enfermagem'
    ),
    (
        'Radiation oncology (London, England)',
        'Radiation Oncology'
    ),
    (
        'J.Neuro-Oncol.',
        'J. Neuro-Oncol.'
    ),
    (
        'Oncology (Williston Park, N.Y.)',
        'ONCOLOGY (United States)'
    ),
    (
        'Journal of Clinical Oncology',
        'Journal of clinical oncology : official journal of the American Society of Clinical Oncology'  # noqa
    ),
    (
        u'Journal of Pain & Palliative Care Pharmacotherapy',
        u'Journal of Pain and Palliative Care Pharmacotherapy'
    ),
    (
        u'Eur.J Cancer Care (Engl.)',
        u'EUR J CANCER CARE'
    )
])
def test_phrase_match(solr, index, query):
    solr.add([{
        'id': '1',
        'phrase_match': index,
    }])

    result = solr.search(
        'phrase_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('phrase_match') for x in result][0]
