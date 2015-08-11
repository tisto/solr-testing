# -*- coding: utf-8 -*-
from fixtures import *
from risparser import risparser
import csv
import os


@pytest.fixture(scope="module", autouse=True)
def load_ris_data(solr):
    solr.delete(q='*:*')
    solr.add(
        parse_risfile(
            'export_information_ris_zell_20150417.txt',
            archive=False
        )
    )
    solr.add(
        parse_risfile(
            'export_palliativ_abgelehnte_20150121.txt',
            archive=True
        )
    )

REGRESSIONS = []
with open('regressions.csv', 'r') as csvfile:
    for row in csv.reader(csvfile, delimiter=';'):
        title = row[0]
        periodical_and_year = row[1].strip()
        periodical_full_name = periodical_and_year[:-4].strip()
        publication_year = periodical_and_year[-4:]
        REGRESSIONS.append({
            'title': title,
            'periodical_full_name': periodical_full_name,
            'publication_year': publication_year
        })


def parse_risfile(filename, archive=False):
    ris_file = os.path.join(
        os.path.dirname(__file__),
        'import',
        filename
    )
    ris_generator = risparser(open(ris_file, 'r'))

    result = []
    for i, item in enumerate(ris_generator):
        result.append({
            'id': i,
            'title': item.get('T1'),
            'periodical_article': item.get('JA'),
            'periodical_full_name': item.get('JF'),
            'year': item.get('Y1'),
            'archive': archive,
        })
    return result


def is_duplicate(solr, ris_dict):
    """Ris Dict:

    {
        'id': 1,
        'title': 'Colorless Green Ideas',
        'periodical_article': 'Journal of Medicine',
        'periodical_full_name': 'Journal of Medicine',
        'year': 2011,
        'archive': True,
    }

    Solr Query:

       title:"Colorless Green Ideas" AND
       periodical_full_name:"Journal of Medicine" AND
       publication_year:"2011"

    """
    # Title
    title = ris_dict.get('title')
    if isinstance(title, unicode):
        # Solr expects utf-8 encoded strings
        title = title.encode('utf-8')
    # Remove double quotes to be able to query the full phrase
    title = title.replace('"', '')
    # Strip prefix whitespace
    title = title.strip()
    query = 'title:"{0}"'.format(title)

    # Journal
    periodical_full_name = ris_dict.get('periodical_full_name')
    if periodical_full_name:
        query += ' AND (periodical_full_name:"{}" OR periodical_full_name:["" TO *] OR periodical_article:"{}" OR periodical_article:["" TO *])'.format(periodical_full_name, periodical_full_name)
    periodical_article = ris_dict.get('periodical_article')
    if periodical_article:
        query += ' OR periodical_article:"{}" OR periodical_article:["" TO *]'.format(periodical_article)
    fq = []

    # Publication Year
    publication_year = ris_dict.get('publication_year')
    if publication_year:
        fq.append('publication_year:{}'.format(publication_year))

    # Archive Flag
    #if archive_flag is not None:
    #    if archive_flag is True:
    #        fq.append("archive_flag:'true'")
    #    else:
    #        fq.append("archive_flag:'false'")

    result = solr.search(query)
    return result.hits > 0


@pytest.mark.parametrize("check", REGRESSIONS)
def test_regressions(solr, check):
    assert is_duplicate(solr, check) == True
