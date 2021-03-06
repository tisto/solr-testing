# -*- coding: utf-8 -*-
from fixtures import *
from pysolr import SolrCoreAdmin
import shutil


@pytest.fixture(scope="module", autouse=True)
def solr(request):
    solr_core = setup_solr_core('publication_match')

    def fin():
        core_admin = SolrCoreAdmin('http://localhost:8989/solr/admin/cores')
        core_admin.unload('publication_match')
        target_dir = 'test-solr/solr/{}'.format('publication_match')
        if os.path.isdir(target_dir):
            shutil.rmtree(target_dir)

    request.addfinalizer(fin)

    return solr_core


@pytest.fixture(scope="function", autouse=True)
def clear_solr(solr_base):
    solr_base.delete(q='*:*')


def test_publication_match_exact(solr):
    solr.add([{
        'id': '1',
        'publication_match': 'Colorless Green Ideas Sleep Furiously',
    }])

    result = solr.search(
        'publication_match:"Colorless Green Ideas Sleep Furiously"'
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_lowercase(solr):
    index = 'Colorless Green Ideas Sleep Furiously'
    query = 'colorless green ideas sleep furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless Green Ideas Sleep Furiously' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_uppercase(solr):
    index = 'colorless green ideas sleep furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'colorless green ideas sleep furiously' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_punctuation(solr):
    index = 'Colorless, Green; Ideas. Sleep: Furiously!'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless, Green; Ideas. Sleep: Furiously!' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_trims_whitespace(solr):
    index = '  Colorless Green Ideas Sleep Furiously         '
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'  Colorless Green Ideas Sleep Furiously         ' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_trims_inner_whitespace(solr):
    index = 'Colorless    Green Ideas Sleep Furiously'
    query = 'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Colorless    Green Ideas Sleep Furiously' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_replaces_non_ascii_characters(solr):
    index = u'Cölorless Grêen Idéaß Slèep Furiously'
    query = u'Colorless Green Ideass Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert u'Cölorless Grêen Idéaß Slèep Furiously' == \
        [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_special_characters(solr):
    index = u'Colorless Green-Ideas Sleep=Furiously #?/[]()'
    query = u'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_content_in_brackets(solr):
    index = u'Colorless Green Ideas Sleep Furiously (or not)'
    query = u'Colorless Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


def test_publication_match_replaces_ampersands_with_and(solr):
    index = u'Colorless & Green Ideas Sleep Furiously'
    query = u'Colorless and Green Ideas Sleep Furiously'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


def test_publication_match_ignores_stopwords(solr):
    index = u'The Cochrane database of systematic reviews'
    query = u'Cochrane database of systematic reviews'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


def test_publication_match_synonyms(solr):
    index = u'Bar'
    query = u'Foo'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


def test_publication_match_phrase_synonyms(solr):
    index = u'Foo Bar'
    query = u'Fizz Buzz'
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]


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
#    (
#       'Journal of Clinical Oncology',
#        'Journal of clinical oncology : official journal of the American Society of Clinical Oncology'  # noqa
#    ),
    (
        u'Journal of Pain & Palliative Care Pharmacotherapy',
        u'Journal of Pain and Palliative Care Pharmacotherapy'
    ),
    (
        u'Eur.J Cancer Care (Engl.)',
        u'EUR J CANCER CARE'
    ),
#    (
#        u'The American journal of hospice & palliative care',
#        u'American Journal of Hospice and Palliative Medicine'
#    ),
    (
        u'The Cochrane database of systematic reviews',
        u'Cochrane database of systematic reviews (Online)'
    ),
    (
        u'Search for evidence-based approaches for the prevention and palliation of hand-foot skin reaction(HFSR) caused by the multikinase inhibitors(MKIs)',  # noqa
        u'Search for evidence-based approaches for the prevention and palliation of hand--foot skin reaction (HFSR) caused by the multikinase inhibitors (MKIs).'  # noqa
    ),
    (
        u'Smoking Cessation in Lung Cancer--Achievable and Effective.',
        u'Smoking cessation in lung cancer - Achievable and effective'
    ),
    (
        u'Academic Medicine',
        u'Acad.Med.'
    ),
    (
        u'Anales de Medicina Especialidades An Med Espec',
        u'An Med Espec'
    ),
    (
        u'Journal; Of, Gastroenterology. And: Hepatology',
        u'Journal Of Gastroenterology And Hepatology',
    )
])
def test_publication_match_regressions(solr, index, query):
    solr.add([{
        'id': '1',
        'publication_match': index,
    }])

    result = solr.search(
        'publication_match:"{}"'.format(query)
    )

    assert 1 == result.hits
    assert index == [x.get('publication_match') for x in result][0]
