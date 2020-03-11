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


from ckan.controllers.organization import OrganizationController
from ckan.common import OrderedDict, c, g, request, _
from urllib import urlencode


import logging
import ckan.model as model
import ckan.lib.base as base
import ckan.logic as logic
import ckan.new_authz as new_authz
import ckan.plugins as plugins
import ckan.lib.helpers as h
import ckan.lib.search as search
import ckan.lib.maintain as maintain
import os, json
from datetime import datetime
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil
from ckanext.ecportal.model.schemas.generic_schema import ResourceValue


render = base.render
abort = base.abort
NotFound = logic.NotFound
NotAuthorized = logic.NotAuthorized
ValidationError = logic.ValidationError
check_access = logic.check_access
get_action = logic.get_action
tuplize_dict = logic.tuplize_dict
clean_dict = logic.clean_dict
parse_params = logic.parse_params
log = logging.getLogger(__name__)


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring)
            else str(v))
            for k, v in params]


def buildRules(result, data, modificationTime):

    for rule in data:
        if rule == 'id':
            break

        if 'id' in data[rule][0]:
            for r in data[rule]:
                result[r['id']] = r
                result[r['id']]['lastUpdate'] = modificationTime
        elif 'rules' in data[rule][0]:
            for r in data[rule]:
                if isinstance([], type(r['rules'])):
                    for s in r['rules']:
                        result[s['id']] = s
                        result[s['id']]['lastUpdate'] = modificationTime
                else:
                    buildRules(result, r['rules'], modificationTime)

    return result

def buildGroups():
    dataset_error_rules_file = os.path.dirname(os.path.abspath(__file__))+'/../../../data/dataset_error_rules.json'
    dataset_error_rules_time = datetime.fromtimestamp(os.path.getmtime(dataset_error_rules_file))
    dataset_error_rules = json.load(open(dataset_error_rules_file))

    dataset_fatal_rules_file = os.path.dirname(os.path.abspath(__file__))+'/../../../data/dataset_fatal_rules.json'
    dataset_fatal_rules_time = datetime.fromtimestamp(os.path.getmtime(dataset_fatal_rules_file))
    dataset_fatal_rules = json.load(open(dataset_fatal_rules_file))

    dataset_warning_rules_file = os.path.dirname(os.path.abspath(__file__))+'/../../../data/dataset_warning_rules.json'
    dataset_warning_rules_time = datetime.fromtimestamp(os.path.getmtime(dataset_warning_rules_file))
    dataset_warning_rules = json.load(open(dataset_warning_rules_file))

    resultFatal = {}
    resultError = {}
    resultWarning = {}

    buildRules(resultFatal, dataset_fatal_rules, dataset_fatal_rules_time)
    buildRules(resultError, dataset_error_rules, dataset_error_rules_time)
    buildRules(resultWarning, dataset_warning_rules, dataset_warning_rules_time)

    return [
        resultFatal,
        resultError,
        resultWarning
    ]

class ECPORTALConfiguration(base.BaseController):


    def vocabularies(self):

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'with_private': False}

        #c.version# = get_action('get_skos_hierarchy')(context, )
        c.lastUpdate
        c.currentVersion
        c.lastModified

        factory = ControlledVocabularyFactory()
        all_mdr = factory.get_all_vocabulary_utils()


        c.nals = []
        for mdr, value in all_mdr.items():
            name = next((lable.value_or_uri for lable in value.schema_concept_scheme.schema.prefLabel_at.values() if lable.lang == 'en'), '')
            uri = value.schema_concept_scheme.uri
            last_update = value.schema_concept_scheme.schema.versionInfo_owl.get('0', ResourceValue('')).value_or_uri
            representation = ''
            c.nals.append({
                'name': name,
                'uri': uri,
                'lastUpdated': last_update,
                'representation': ''
            })


        return render('configuration/vocabularies.html')

    def validationRules(self):

        context = {'model': model, 'session': model.Session,
                   'user': c.user, 'for_view': True,
                   'with_private': False}

        #c.version# = get_action('get_skos_hierarchy')(context, max_element)
        c.groups = buildGroups()

        return render('configuration/validation.html')
