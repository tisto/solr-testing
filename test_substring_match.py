# -*- coding: utf-8 -*-
from fixtures import *
from pysolr import SolrCoreAdmin
import pytest
import shutil


@pytest.fixture(scope="module", autouse=True)
def solr(request, solr_core_name='substring_match'):
    solr_core = setup_solr_core(solr_core_name)

    def fin():
        core_admin = SolrCoreAdmin('http://localhost:8989/solr/admin/cores')
        core_admin.unload(solr_core_name)
        target_dir = 'test-solr/solr/{}'.format(solr_core_name)
        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)

    request.addfinalizer(fin)

    return solr_core


@pytest.fixture(scope="function", autouse=True)
def clear_solr(solr_base):
    solr_base.delete(q='*:*')


def test_substring_match_exact(solr):
    solr.add([{
        'id': '1',
        'substring_match': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'substring_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_ignores_lowercase(solr):
    index = 'Colorless Green Ideas Sleep Furiously'
    query = 'colorless green ideas sleep furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_ignores_uppercase(solr):
    index = 'colorless green ideas sleep furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'colorless green ideas sleep furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_ignores_punctuation(solr):
    index = 'Colorless, Green; Ideas. Sleep? Furiously!'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless, Green; Ideas. Sleep? Furiously!' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_trims_whitespace(solr):
    index = '  Colorless Green Ideas Sleep Furiously         '
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'  Colorless Green Ideas Sleep Furiously         ' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_trims_inner_whitespace(solr):
    index = 'Colorless    Green Ideas Sleep Furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless    Green Ideas Sleep Furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_replaces_non_ascii_characters(solr):
    index = u'Cölorless Grêen Idéaß Slèep Furiously'
    query = u'Colorless Green Ideass Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Cölorless Grêen Idéaß Slèep Furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_ignores_special_characters(solr):
    index = u'Colorless Green-Ideas Sleep=Furiously #?/[]()'
    query = u'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'substring_match': index,
    }])

    result = solr.search(
        'substring_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('substring_match') for x in result][0]


def test_substring_match_finds_prefix(solr):
    solr.add([{
        'id': '1',
        'substring_match': 'Colorless',
    }])

    result = solr.search(
        'substring_match:"Color"'
    )

    assert 1 == result.hits
    assert u'Colorless' == [x.get('substring_match') for x in result][0]


def test_substring_finds_prefix_in_phrase(solr):
    solr.add([{
        'id': '1',
        'substring_match': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'substring_match:"Color"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('substring_match') for x in result][0]


def test_substring_match_does_not_find_prefix_in_search(solr):
    """When N-grams are created during search. The result contains elements for
       all possible substrings of the search query. This is not what the user
       would expect.
    """
    solr.add([{
        'id': '1',
        'substring_match': 'Colorless Green Ideas Sleep Furiously',
    }])
    solr.add([{
        'id': '2',
        'substring_match': 'Color',
    }])

    result = solr.search(
        'substring_match:"Colorless"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('substring_match') for x in result][0]


# @pytest.mark.skip(
#     reason='Suffix match would require a 2nd idx with EdgeNGram side=back'
# )
# def test_substring_match_finds_suffix(solr):
#     solr.add([{
#         'id': '1',
#         'substring_match': 'Colorless',
#     }])
#
#     result = solr.search(
#         'substring_match:"less"'
#     )
#
#     assert 1 == result.hits
#     assert u'Colorless' == [x.get('substring_match') for x in result][0]
#
