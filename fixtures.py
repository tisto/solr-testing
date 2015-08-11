# -*- coding: utf-8 -*-
from fixtures import *

import subprocess
import pysolr
import pytest
import requests
import time
import urllib2
import os
import shutil
import signal
import sys


TEST_DIR = 'test-solr'
SOLR_BASE_URL = 'http://localhost:8989/solr'
SOLR_PING_URL = 'http://localhost:8989/solr/admin/ping'
SOLR_PORT = '8989'
SOLR_TIMEOUT = 10
SOLR_START_CMD = 'java -Djetty.port={} -jar start.jar'.format(SOLR_PORT)


def setup_solr_core(solr_core, schema_xml=None, solrconfig_xml=None):
    """Set up a Solr core for testing. Try to look up custom solrconfig.xml and
       schema.xml from the templates directory. e.g. a custom 'phrase_match'
       schema would have the filename 'phrase_match-schema.xml' and the
       solrconfig would have the filename 'phrase_match-solrconfig.xml.'
    """
    source_dir = 'test-solr/solr/collection1'
    target_dir = 'test-solr/solr/{}'.format(solr_core)
    # Remove old core dir if it exists
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
    # Make a copy of the collection1 core
    shutil.copytree(
        source_dir,
        target_dir
    )

    # Remove core.properties from new core (requirement to add a new core)
    if os.path.isfile('{}/core.properties'.format(target_dir)):
        os.remove('{}/core.properties'.format(target_dir))
    # Load solrconfig.xml if file exists
    if not solrconfig_xml:
        solrconfig_xml = '{}-solrconfig.xml'.format(solr_core)
    if os.path.isfile('templates/{}'.format(solrconfig_xml)):
        prepare_solrconfig(solrconfig_xml, solr_core)
    # Load schema.xml if file exists
    if not schema_xml:
        schema_xml = '{}-schema.xml'.format(solr_core)
    if os.path.isfile('templates/{}'.format(schema_xml)):
        prepare_schema(schema_xml, solr_core)
    # Prepare stopwords
    prepare_stopwords_txt(solr_core)

    # Register the new core in Solr
    #core_admin = pysolr.SolrCoreAdmin('http://localhost:8989/solr/admin/cores')
    #core_admin.create('phrase_match')
    response = requests.get(
        'http://localhost:8989/solr/' +
        'admin/cores?action=CREATE' +
        '&name={}'.format(solr_core) +
        '&instanceDir={}'.format(solr_core)
    )

    if response.status_code != 200:
        raise
    solr = pysolr.Solr(SOLR_BASE_URL + '/' + solr_core, timeout=SOLR_TIMEOUT)
    return solr


def prepare_solrconfig(solrconfig_xml, solr_core):
    with open('templates/{}'.format(solrconfig_xml), 'r') as template:
        with open(
            'test-solr/solr/{}/conf/solrconfig.xml'.format(solr_core),
            'w'
        ) as solrconfig:
            solrconfig.write(template.read())


def prepare_schema(schema_xml, solr_core):
    with open('templates/{}'.format(schema_xml), 'r') as template:
        with open(
            'test-solr/solr/{}/conf/schema.xml'.format(solr_core),
            'w'
        ) as schema:
            schema.write(template.read())


def prepare_stopwords_txt(solr_core):
    with open('templates/stopwords.txt') as template:
        with open(
            'test-solr/solr/{}/conf/stopwords.txt'.format(solr_core),
            'w'
        ) as schema:
            schema.write(template.read())


@pytest.fixture(scope="session", autouse=True)
def solr_base(request):
    devnull = open('/dev/null', 'w')
    solr_process = subprocess.Popen(
        SOLR_START_CMD,
        stdout=devnull,
        stderr=devnull,
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
    solr = pysolr.Solr(SOLR_BASE_URL, timeout=SOLR_TIMEOUT)
    return solr
