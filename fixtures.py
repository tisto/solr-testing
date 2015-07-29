# -*- coding: utf-8 -*-
from fixtures import *

import subprocess
import pysolr
import pytest
import time
import urllib2
import os
import shutil
import signal
import sys

TEST_DIR = 'test-solr'
SOLR_URL = 'http://localhost:8989/solr'
SOLR_PING_URL = 'http://localhost:8989/solr/admin/ping'
SOLR_PORT = '8989'
SOLR_START_CMD = 'java -Djetty.port={} -jar start.jar'.format(SOLR_PORT)


def setup_solr_core(solr_core):
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
    # Write core.properties configuration file
    with open('{}/core.properties'.format(target_dir), 'r+') as core_properties:  # noqa
        core_properties.seek(0)
        core_properties.write('name={}'.format(solr_core))


def prepare_solrconfig(solrconfig_xml='solrconfig.xml'):
    with open('templates/{}'.format(solrconfig_xml), 'r') as template:
        with open(
            'test-solr/solr/collection1/conf/solrconfig.xml',
            'w'
        ) as solrconfig:
            solrconfig.write(template.read())


def prepare_schema(schema_xml='schema.xml'):
    with open('templates/{}'.format(schema_xml), 'r') as template:
        with open(
            'test-solr/solr/collection1/conf/schema.xml',
            'w'
        ) as schema:
            schema.write(template.read())


@pytest.fixture(scope="module", autouse=True)
def solr(request):
    setup_solr_core('phrase_match')
    prepare_solrconfig()
    prepare_schema('phrase_match-schema.xml')
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
