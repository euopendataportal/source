#    Copyright (C) <2018>  <Publications Office of the European Union>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>

'''
Created on 24 Sep 2014

@author: grouesva
'''

import logging
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.util import guess_format
from rdflib import URIRef
from codecs import open as codecsOpen
from json import dumps
from urllib2 import URLError
import csv

log = logging.getLogger()

PREF_LABEL_URI = URIRef('http://www.w3.org/2004/02/skos/core#prefLabel')
HEAD = { 'vars': ['term', 'label', 'language']}
THESAURUS_CONCEPT_URI = 'http://eurovoc.europa.eu/schema#ThesaurusConcept'
DOMAINS_URI = 'http://eurovoc.europa.eu/schema#Domain'

def create_graph(eurovoc_file):
    '''
    Parse the EuroVoc export and load it as an RDFlib Graph
    :param eurovoc_file: the rdf/xml or ntriple EuroVoc file
    '''
    g = Graph()
    log.info('Parsing EuroVoc file (this can take several minutes)...')
    try:
        g.parse(eurovoc_file, format=guess_format(eurovoc_file))
        log.info('Done')
        log.info('%s triples loaded' % len(g))
    except URLError:
        log.error( "Couldn't parse the file ", eurovoc_file)
        raise
    return g


def write_json(output_file, bindings):
    '''
     Write the tags contains in bindings in JSON into the file output_file
    :param output_file: the file path to write to
    :param bindings: the dict containing the tags uris, labels and languages
    '''
    results = { 'bindings': bindings}
    output = {'HEAD': HEAD, 'results':results}
    try:
        with codecsOpen(output_file,'w','utf-8') as f:
            f.write(dumps(output, ensure_ascii= False, indent = 2, encoding='utf-8'))
    except URLError:
        log.info("Couldn't save to the file ", output_file)

def create_eurovoc_json(eurovoc_file, concepts_file=None, domains_file=None, domains_translations=None, thesaurus_concept=THESAURUS_CONCEPT_URI, domain=DOMAINS_URI):
    '''
        Parse the eurovoc_file, retrieve the EuroVoc concepts and domains and convert in JSON
    :param eurovoc_file: the rdf/xml or ntriple EuroVoc file
    :param concepts_file: the file where the JSON for concepts will be stored
    :param domains_file: the file where the JSON for domains will be stored
    :param thesaurus_concept: the URI of the EuroVoc concept class
    :param domain: the URI of the EuroVoc domain class
    '''
    global translations
    if domains_translations == None:
        translations = None
    else:
	translations = translationsFromCsv(domains_translations)
    try:
        g = create_graph(eurovoc_file)
        if concepts_file != None:
            bindings = create_tags(g, thesaurus_concept)
            write_json(concepts_file, bindings)
        if domains_file != None:
            bindings = create_tags(g, domain, 3)
            write_json(domains_file, bindings)
    except URLError:
        log.error('The JSON files were not produced!')
    except Exception as e:
        import traceback
        log.error(traceback.print_exc())


def create_tags(graph, uri, isDomains = None):
    '''
    Create the dict for the instance of uri contained in the graph
    :param graph:
    :param uri:
    '''
    global translations
    class_uri_ref = URIRef(uri)
    bindings = []
    for s, _ , _ in graph.triples( (None, RDF.type, class_uri_ref ) ):
        log.info("%s is a %s, will now retrieve labels" % (s , class_uri_ref))
        term = { 'type': 'uri', 'value': s}
        labels = graph.preferredLabel(s, None, None, (PREF_LABEL_URI,))
        if translations != None:
	   #we look for the english key
	   for _ , literal in labels:
             if literal.language == 'en':
                 english_key=literal[3:]
                 break
	for _ , literal in labels:
            if isDomains != None:
                lit = literal[3:]
	    else:
		lit = literal
            if translations == None or isDomains == None:
		if isDomains == None:
                     translated_label = lit
                else:
                   translated_label = lit.lower()
	    else:
		key = translations.get(english_key,None)
		if key == None:
		    log.info("no translations from csv found for "+english_key+" for "+literal.language)
		    translated_label = lit.lower()
		else:
		    translated_label = key.get(literal.language,None)
		    if translated_label == None:
		        log.info("no translations from csv found for "+english_key+" for "+literal.language)
			translated_label = lit
            label = { 'type': 'literal', 'value': translated_label}
            language = { 'type': 'literal', 'value': literal.language}
            result = {'term': term, 'label':label,'language':language}
            bindings.append(result)
    if len(bindings)==0:
        log.warn(u'No instances found for class {0}'.format(uri))
    return bindings

def translationsFromCsv(csv_path):

    with open(csv_path,'rb') as csvfile:
        spamreader = csv.reader(csvfile,delimiter=';')
        keys = []
        languages = []
        translations = {}
        for count_row, row in enumerate(spamreader):
            for count_entry, entry in enumerate(row):
                if count_row == 0 and count_entry == 0:
                    continue
                if count_row != 0 and count_entry == 0:
                    key = entry.strip()
                    keys.append(key)
                    translations[key]={}
                else:
                    if count_row == 0 and count_entry != 0:
                        languages.append(entry.strip().lower())
                    else:
                        translations[key][languages[count_entry-1]]=entry.strip().decode('utf-8')
    return translations
