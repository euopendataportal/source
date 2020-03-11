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

import logging
import collections
import os
import sys
import csv
import ujson as json
import re

from ckan.logic import (tuplize_dict,
                        clean_dict)
from ckan.lib.navl.dictization_functions import unflatten
import ckan
import ckan.plugins as plugins
import ckan.model as model
import ckan.logic as logic
import ckan.lib.cli as cli
import ckanext.ecportal.forms as forms
import ckanext.ecportal.searchcloud as searchcloud
import ckanext.ecportal.rdfutil as rdfutil
import lxml.etree
import ckanext.ecportal.rdf2json as rdf2json
import rdfutil

log = logging.getLogger()


class InvalidDateFormat(Exception):
    pass


class ECPortalCommand(cli.CkanCommand):
    '''
    Commands:
        paster ecportal update-publishers <file (optional)> -c <config>
        paster ecportal migrate-publisher <source> <target> -c <config>
        paster ecportal migrate-odp-namespace -c <config>
        paster ecportal export-datasets <folder> -c <config>
        paster ecportal import-csv-translations -c <config>
        paster ecportal import-csv-translations-licence -c <config>

        paster ecportal update-all-vocabs -c <config>
        paster ecportal delete-all-vocabs -c <config>

        paster ecportal update-geo-vocab <file (optional)> -c <config>
        paster ecportal update-dataset-type-vocab <file (optional)> -c <config>
        paster ecportal update-language-vocab <file (optional)> -c <config>
        paster ecportal update-status-vocab <file (optional)> -c <config>
        paster ecportal update-interop-vocab <file (optional)> -c <config>
        paster ecportal update-temporal-vocab <file (optional)> -c <config>
        paster ecportal update-eurovoc-domains-vocab <file (optional)> -c <config>
        paster ecportal update-eurovoc-concepts-vocab <file (optional)> -c <config>

        paster ecportal delete-geo-vocab -c <config>
        paster ecportal delete-dataset-type-vocab -c <config>
        paster ecportal delete-language-vocab -c <config>
        paster ecportal delete-status-vocab -c <config>
        paster ecportal delete-interop-vocab -c <config>
        paster ecportal delete-temporal-vocab -c <config>
        paster ecportal delete-eurovoc-domains-vocab -c <config>
        paster ecportal delete-eurovoc-concepts-vocab -c <config>

        paster ecportal purge-package-extra-revision -c <config>
        paster ecportal purge-task-data -c <config>

        paster ecportal searchcloud-install-tables -c <config>
        paster ecportal searchcloud-generate-unapproved-search-list -c <config>

        paster ecportal create-json-eurovoc-concepts <source_eurovoc (optional)> <target_concepts (optional)> <thesaurus_concept_uri (optional)> <domain_uri (optional)> -c <config>
        paster ecportal create-json-eurovoc-domains <source_eurovoc (optional)> <target_domains (optional)> <thesaurus_concept_uri (optional)> <domain_uri (optional)> -c <config>
        paster ecportal create-json-eurovoc-all <source_eurovoc (optional)> <target_concepts (optional)> <target_domains (optional)> <thesaurus_concept_uri (optional)> <domain_uri (optional)> -c <config>

    Where:
        <data> = path to XML file (format of the Eurostat bulk import metadata)
        <user> = perform actions as this CKAN user (name)
        <publisher> = a publisher name or ID
        <folder> = Output folder for dataset export
        <file> = (optional) path to input JSON or CSV file. If not specified,
                 the default files in the /data directory are used.
        <config> = path to your ckan config file
        <source_eurovoc> = (optional) rdf/xml or ntriple EuroVoc export
        <target_concepts> = (optional) path to the JSON file to produce for concepts
        <target_domains> = (optional) path to the JSON file to produce for domains
        <thesaurus_concept_uri> = (optional) URI of the Concept class in EuroVoc
        <domain_uri> = (optional) URI of the Domain class in EuroVoc

    The commands should be run from the ckanext-ecportal directory.
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    default_data_dir = os.path.dirname(os.path.abspath(__file__))
    default_file = {
        forms.DATASET_TYPE_VOCAB_NAME:
        default_data_dir + '/../../data/odp-dataset-type.json',
        forms.EUROVOC_DOMAINS_VOCAB_NAME:
        default_data_dir + '/../../data/eurovoc_domains.json',
        forms.EUROVOC_CONCEPTS_VOCAB_NAME:
        default_data_dir + '/../../data/eurovoc_concepts.json',
        forms.GEO_VOCAB_NAME:
        default_data_dir + '/../../data/po-countries.json',
        forms.INTEROP_VOCAB_NAME:
        default_data_dir + '/../../data/odp-interoperability-level.json',
        forms.LANGUAGE_VOCAB_NAME:
        default_data_dir + '/../../data/po-languages.json',
        forms.STATUS_VOCAB_NAME:
        default_data_dir + '/../../data/odp-dataset-status.json',
        forms.TEMPORAL_VOCAB_NAME:
        default_data_dir + '/../../data/odp-temporal-granularity.json',
        'publishers': default_data_dir + '/../../data/po-corporate-bodies.json',
        'eurovoc_source': default_data_dir + '/../../data/eurovoc_skos.rdf',
        'domains_translations': default_data_dir + '/../../data/eurovoc_domains.csv'
    }


    def _create_json_eurovoc_tags(self, eurovoc_path, concepts_file, domains_file, thesaurus_uri=None, domains_uri=None, domains_translations=None):
        if not os.path.exists(eurovoc_path):
            log.error('File {0} does not exist'.format(eurovoc_path))
            sys.exit(1)
        print 'EuroVoc source file: ', eurovoc_path
        if concepts_file != None:
            print 'Path to the output JSON file for concepts: ', concepts_file
        if domains_file != None:
            print 'Path to the output JSON file for domains: ', domains_file
        if thesaurus_uri != None:
            print 'The following class will be used to retrieve concepts: ', thesaurus_uri
        if domains_uri != None:
            print 'The following class will be used to retrieve domains: ', domains_uri
        if domains_translations != None:
            print 'The following file will be used to retrieve domains translations: ', domains_translations
        rdf2json.create_eurovoc_json(eurovoc_path, concepts_file, domains_file,domains_translations)

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print ECPortalCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        user = plugins.toolkit.get_action('get_site_user')(
            {'model': model, 'ignore_auth': True}, {}
        )
        self.user_name = user['name']

        # file_path is used by update-vocab and update-publishers commands
        file_path = self.args[1] if len(self.args) >= 2 else None

        if cmd == 'update-publishers':
            self.update_publishers(file_path)

        elif cmd == 'migrate-publisher':
            if len(self.args) != 3:
                print ECPortalCommand.__doc__
                return
            self.migrate_publisher(self.args[1], self.args[2])

        elif cmd == 'update-geo-vocab':
            self.update_vocab_from_file(forms.GEO_VOCAB_NAME, file_path)

        elif cmd == 'migrate-odp-namespace':
            self.odp_namespace()

        elif cmd == 'delete-geo-vocab':
            self._delete_vocab(forms.GEO_VOCAB_NAME)

        elif cmd == 'update-dataset-type-vocab':
            self.update_vocab_from_file(forms.DATASET_TYPE_VOCAB_NAME, file_path)

        elif cmd == 'delete-dataset-type-vocab':
            self._delete_vocab(forms.DATASET_TYPE_VOCAB_NAME)

        elif cmd == 'create-json-eurovoc-all':
            eurovoc_path = self.args[1] if len(self.args) >= 2 else self.default_file['eurovoc_source']
            concepts_json_path = self.args[2] if len(self.args) >= 3 else self.default_file[forms.EUROVOC_CONCEPTS_VOCAB_NAME]
            domain_json_path = self.args[3] if len(self.args) >= 4 else self.default_file[forms.EUROVOC_DOMAINS_VOCAB_NAME]
            concept_uri = self.args[4] if len(self.args) >= 5 else rdf2json.THESAURUS_CONCEPT_URI
            domain_uri = self.args[5] if len(self.args) >= 6 else rdf2json.DOMAINS_URI
            self._create_json_eurovoc_tags(eurovoc_path, concepts_json_path, domain_json_path, concept_uri, domain_uri)

        elif cmd == 'create-json-eurovoc-concepts':
            eurovoc_path = self.args[1] if len(self.args) >= 2 else self.default_file['eurovoc_source']
            concepts_json_path = self.args[2] if len(self.args) >= 3 else self.default_file[forms.EUROVOC_CONCEPTS_VOCAB_NAME]
            concept_uri = self.args[3] if len(self.args) >= 4 else rdf2json.THESAURUS_CONCEPT_URI
            self._create_json_eurovoc_tags(eurovoc_path, concepts_json_path, None, concept_uri)

        elif cmd == 'create-json-eurovoc-domains':
            eurovoc_path = self.args[1] if len(self.args) >= 2 else self.default_file['eurovoc_source']
            domain_json_path = self.args[2] if len(self.args) >= 3 else self.default_file[forms.EUROVOC_DOMAINS_VOCAB_NAME]
            domain_uri = self.args[3] if len(self.args) >= 4 else rdf2json.DOMAINS_URI
            eurovoc_translations_path = self.args[4] if len(self.args) >= 5 else self.default_file['domains_translations']
            self._create_json_eurovoc_tags(eurovoc_path, None, domains_file=domain_json_path, domains_uri=domain_uri, domains_translations=eurovoc_translations_path)

        elif cmd == 'update-eurovoc-domains-vocab':
            self.update_vocab_from_file(forms.EUROVOC_DOMAINS_VOCAB_NAME, file_path)

        elif cmd == 'update-eurovoc-concepts-vocab':
            self.update_vocab_from_file(forms.EUROVOC_CONCEPTS_VOCAB_NAME, file_path)

        elif cmd == 'delete-eurovoc-domains-vocab':
            self._delete_vocab(forms.EUROVOC_DOMAINS_VOCAB_NAME)

        elif cmd == 'delete-eurovoc-concepts-vocab':
            self._delete_vocab(forms.EUROVOC_CONCEPTS_VOCAB_NAME)

        elif cmd == 'update-language-vocab':
            self.update_vocab_from_file(forms.LANGUAGE_VOCAB_NAME, file_path)

        elif cmd == 'delete-language-vocab':
            self._delete_vocab(forms.LANGUAGE_VOCAB_NAME)

        elif cmd == 'update-status-vocab':
            self.update_vocab_from_file(forms.STATUS_VOCAB_NAME, file_path)

        elif cmd == 'delete-status-vocab':
            self._delete_vocab(forms.STATUS_VOCAB_NAME)

        elif cmd == 'update-interop-vocab':
            self.update_vocab_from_file(forms.INTEROP_VOCAB_NAME, file_path)

        elif cmd == 'delete-interop-vocab':
            self._delete_vocab(forms.INTEROP_VOCAB_NAME)

        elif cmd == 'update-temporal-vocab':
            self.update_vocab_from_file(forms.TEMPORAL_VOCAB_NAME, file_path)

        elif cmd == 'delete-temporal-vocab':
            self._delete_vocab(forms.TEMPORAL_VOCAB_NAME)

        elif cmd == 'update-all-vocabs':
            self.update_all_vocabs()

        elif cmd == 'delete-all-vocabs':
            self.delete_all_vocabs()

        elif cmd == 'purge-package-extra-revision':
            self.purge_package_extra_revision()

        elif cmd == 'purge-task-data':
            self.purge_task_data()

        elif cmd == 'searchcloud-install-tables':
            self.searchcloud_install_tables()

        elif cmd == 'searchcloud-generate-unapproved-search-list':
            self.searchcloud_generate_unapproved_search_list()

        elif cmd == 'import-csv-translations':
            self.import_csv_translation()

        elif cmd == 'import-csv-translations-licence':
            self.import_csv_translation_licence()

        else:
            log.error('Command "%s" not recognized' % (cmd,))

    def _read_publishers_from_file(self, file_path=None):
        if not file_path:
            file_path = self.default_file['publishers']
        if not os.path.exists(file_path):
            log.error('File {0} does not exist'.format(file_path))
            sys.exit(1)

        with open(file_path) as json_file:
            full_json = json.loads(json_file.read())

        return list(self._parse_publishers_from(full_json))

    def _add_publishers(self, publishers):
        log.info('Creating CKAN publisher (organization) objects')

        organizations_title_lookup = {}

        for publisher in publishers:
            context = {'model': model,
                       'session': model.Session,
                       'user': self.user_name}
            try:
                if publisher.lang_code == 'en':
                    organization = {'name': publisher.name,
                             'title': publisher.title,
                             'type': u'organization'}
                    plugins.toolkit.get_action('organization_create')(context, organization)
                    log.info('Added new publisher: %s [%s]',
                             publisher.title, publisher.name)
                    organizations_title_lookup[publisher.name] = \
                        publisher.title or publisher.name
            except:
                log.error("Validation Error with organization '%s'! Publisher is already deleted. Check you data to import!" % publisher.name)


        self._update_translations(publishers, organizations_title_lookup)

    _Publisher = collections.namedtuple('Publisher', 'name title lang_code')

    def _parse_publishers_from(self, data):
        for item in data['results']['bindings']:
            yield self._Publisher(
                name=item['term']['value'].split('/')[-1].lower(),
                title=item['label']['value'],
                lang_code=item['language']['value'])


    def migrate_publisher(self, source_publisher_name, target_publisher_name):
        '''
        Migrate datasets and users from one publisher to another.
        '''
        context = {'model': model,
                   'session': model.Session,
                   'ecodp_with_package_list': True,
                   'ecodp_update_packages': True,
                   'user': self.user_name}

        source_publisher_name = source_publisher_name.lower()
        target_publisher_name = target_publisher_name.lower()

        source_publisher = plugins.toolkit.get_action('organization_show')(
            context, {'id': source_publisher_name})

        target_publisher = plugins.toolkit.get_action('organization_show')(
            context, {'id': target_publisher_name})

        # Migrate users
        source_users = self._extract_members(source_publisher['users'])
        target_users = self._extract_members(target_publisher['users'])

        source_publisher['users'] = []
        target_publisher['users'] = self._migrate_user_lists(source_users,
                                                             target_users)

        # Migrate datasets
        source_datasets = self._extract_members(source_publisher['packages'])
        target_datasets = self._extract_members(target_publisher['packages'])

        source_publisher['packages'] = []
        target_publisher['packages'] = self._migrate_dataset_lists(source_datasets, target_datasets)

        for package in target_publisher['packages']:
            realPackage = plugins.toolkit.get_action('package_show')(context, {u"id":package['name']})
            if realPackage != None and 'rdf' in realPackage:
                self._replace_publisher(r'(?P<publisher>\<dct:publisher\>.*\<skos\:Concept.?rdf\:about=[^\\\"]*.*\<\/dct\:publisher\>)', realPackage, source_publisher_name.upper(), target_publisher_name.upper())
                self._replace_publisher(r'(?P<publisher>\<ecodp\:contactPoint\>\\n.*ecodp\:contactPoint\>)', realPackage, ">"+source_publisher_name.upper()+"<",  ">"+target_publisher_name.upper()+"<")

        # Clean data
        source_publisher.pop('display_name', None)
        target_publisher.pop('display_name', None)

        # Perform the updates (on organization and on package side)
        # TODO: make these ones atomic action. (defer_commit)
        plugins.toolkit.get_action('organization_update')(context, source_publisher)
        plugins.toolkit.get_action('organization_update')(context, target_publisher)

        # Update the owner_org info in the package related DB tables (due to session management not possible in loop above)
        # --> maybe a bit inefficient...
        for package in target_publisher['packages']:
            data_dict = {'id': package['name'], 'organization_id': target_publisher_name}
            plugins.toolkit.get_action('package_owner_org_update')(context, data_dict)


    def _replace_publisher(self, search_regex, realPackage, source_publisher_name, target_publisher_name):
        '''
            Search for a pattern in the rdf xml value of the package and replaces it via the db replace function
            :search_regex: The search regular expression to find the value in the rdf tag
            :realPackage: the whole package object
            :source_publisher_name: the source publisher name must be in upper case and if necessary with xml marks
            :target_publisher_name: the target publisher name must be in upper case and if necessary with xml marks
        '''
        update_query = '''
        begin;

        update package_extra set value =
               replace(value, :source, :target)
           where key = :key
             and package_id = (Select id from package where name = :name);

        update package_extra_revision set value =
               replace(value, :source, :target)
           where key = :key
             and package_id = (Select id from package_revision where name = :name);
        commit;
        '''

        source_publisher_grp = re.search(search_regex, realPackage['rdf'], re.MULTILINE)
        if source_publisher_grp != None:
            source_publisher_tag = source_publisher_grp.group('publisher')
            if source_publisher_name in source_publisher_tag:
                target_publisher_tag = re.sub(source_publisher_name, target_publisher_name, source_publisher_tag)
                if target_publisher_tag != source_publisher_tag:
                    log.info("Publisher RDF value '%s' will be replaced with '%s'" %(source_publisher_tag, target_publisher_tag))
                    model.Session.execute(update_query, params={"source": source_publisher_tag, "target": target_publisher_tag, "key":"rdf","name":realPackage['name']})


    def setup_namespaces(self, root):
        local_namespaces = {
            'http://purl.org/dc/terms/#': 'dct',
            'http://www.w3.org/1999/02/22-rdf-syntax-ns#': 'rdf',
            'http://www.w3.org/ns/dcat#': 'dcat',
            'http://data.europa.eu/euodp/ontologies/ec-odp#': 'ecodp',
            'http://xmlns.com/foaf/0.1/#': 'foaf'
        }
        local_ns = dict((v, k) for k, v in local_namespaces.iteritems())
        for k, v in root.nsmap.iteritems():
            if v in local_namespaces:
                local_ns[local_namespaces[v]] = v
        return local_ns

    def odp_namespace(self):
        # remove all catalog records
        log.info('Starting ODP namespace migration')
        log.info('Removing old catalog records (RDF)')

        for table in ['package_extra', 'package_extra_revision']:
            sql = '''select id, package_id, value from %s
                     where key = 'rdf' and value like '%%record%%' ''' % table
            result = model.Session.execute(sql)
            for id, package_id, rdf in result:
                rdf = json.loads(rdf)
                try:
                    root = lxml.etree.fromstring(rdf.encode('utf-8'))
                except lxml.etree.XMLSyntaxError:
                    continue

                namespaces = self.setup_namespaces(root)
                results = root.xpath('//rdf:Description/dcat:record',
                                     namespaces=namespaces)
                for record in results:
                    description = record.getparent()
                    parent = description.getparent()
                    parent.remove(description)

                results = root.xpath('//dcat:Catalog',
                                     namespaces=namespaces)
                for record in results:
                    parent = record.getparent()
                    parent.remove(record)

                sql = '''update %s set value = :value where id = :id''' % table
                model.Session.execute(sql, params={
                    "value": json.dumps(lxml.etree.tostring(root)),
                    "id": id})
                model.Session.commit()

        # add catalog records back
        log.info('Adding updated catalog records (RDF)')

        for table in ['package_extra', 'package_extra_revision']:
            sql = '''select pe.id, p.name, value from %s pe
                     join package p on p.id = pe.package_id
                     where key = 'rdf' ''' % table
            result = model.Session.execute(sql)
            for id, name, rdf in result:
                rdf = json.loads(rdf)
                origin_url, updated_rdf = rdfutil.update_rdf(
                    rdf, name, {'model': model})
                sql = '''update %s set value = :value where id = :id''' % table
                if updated_rdf:
                    model.Session.execute(sql, params={
                        "value": json.dumps(updated_rdf),
                        "id": id})

        log.info('Updating metadata')
        sql = '''
        begin;

        update tag set name =
            replace(name,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where name like '%http://open-data.europa.eu%';

        update term_translation set term =
            replace(term,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where term like '%http://open-data.europa.eu%';

        update resource set resource_type =
            replace(resource_type,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where resource_type like '%http://open-data.europa.eu%';

        update resource_revision set resource_type =
            replace(resource_type,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where resource_type like '%http://open-data.europa.eu%';

        update resource set resource_type =
            'http://data.europa.eu/euodp/kos/documentation-type/Visualization'
        where resource_type = 'Visualization';

        update resource_revision set resource_type =
            'http://data.europa.eu/euodp/kos/documentation-type/Visualization'
        where resource_type = 'Visualization';

        update package_extra set value =
            replace(value,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where value like '%http://open-data.europa.eu%';

        update package_extra_revision set value =
            replace(value,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where value like '%http://open-data.europa.eu%';

        update package set license_id =
            replace(license_id,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where license_id like '%http://open-data.europa.eu%';

        update package_revision set license_id =
            replace(license_id,
                    'http://open-data.europa.eu',
                    'http://data.europa.eu/euodp')
        where license_id like '%http://open-data.europa.eu%';

        commit;
        '''
        model.Session.execute(sql)

    def _extract_members(self, members):
        '''Strips redundant information from members of a group'''
        return [{'name': member['name'],
                 'capacity': member['capacity']}
                for member in members]

    def _migrate_dataset_lists(self, source_datasets, target_datasets):
        '''Migrate datasets from source into target.

        Returns a new list leaving original lists untouched.

        The merging retains the strictest capacity.  That is, if the same
        dataset is 'private' in either list, it will remain private in the
        result.
        '''
        VALID_CAPACITIES = ['private', 'public']

        def user_capacity_merger(c1, c2):
            assert c1 in VALID_CAPACITIES
            assert c2 in VALID_CAPACITIES
            if c1 == c2:
                return c1
            else:
                return 'private'  # assume just two valid capicities

        return self._merge_members(source_datasets,
                                   target_datasets,
                                   user_capacity_merger)

    def _migrate_user_lists(self, source_users, target_users):
        '''Migrate users from source into target.

        Returns a new list leaving original lists untouched.

        The merging is quite simple, and retains user's permissions for both
        lists.

            - The target list will not lose any users.
            - Source users will be added to the target with the highest
              capacity of membership that the user has in either list.  Ie - If
              a user is an admin in the source list, they will become an admin
              in the target list.  Or if a user is an admin in the target list,
              they will retain that capacity, regardless of capacity in the
              source list.
         '''
        VALID_CAPACITIES = ['admin', 'editor']

        def user_capacity_merger(c1, c2):
            assert c1 in VALID_CAPACITIES
            assert c2 in VALID_CAPACITIES
            if c1 == c2:
                return c1
            else:
                return 'admin'  # assume just two valid capicities

        return self._merge_members(source_users,
                                   target_users,
                                   user_capacity_merger)

    def _merge_members(self, source_members, target_members, capacity_merger):
        '''Migrates members from source into target.

        Returns a new list, leaving original lists (and member dicts)
        untouched.

        If the member is found in both lists, then the member's new capacity
        is handled by the ``capacity_merger`` function.

        :param source_members: List of member dicts
        :param target_members: List of member dicts
        :param capacity_merger: Function
                (source_capacity, target_capacity) -> merged_capacity
        '''
        source_member_names = set(member['name'] for member in source_members)
        target_member_names = set(member['name'] for member in target_members)

        target_capacities = dict((member['name'], member['capacity'])
                                 for member in target_members)

        result = [member.copy() for member in target_members
                  if member['name'] not in source_member_names]

        result += [member.copy() for member in source_members
                   if member['name'] not in target_member_names]

        for member in source_members:
            name = member['name']
            if name not in target_member_names:
                continue

            member = member.copy()
            source_capacity = member['capacity']
            target_capacity = target_capacities[name]
            member['capacity'] = capacity_merger(source_capacity,
                                                 target_capacity)

            if source_capacity != target_capacity:
                log.warn('Mismatched member capacities: '
                         '%s will be migrated as %s'
                         % (name, member['capacity']))

            result.append(member)

        return result

    def update_publishers(self, file_path=None):
        '''
        Update existing publisher organizations.

         - new publishers are added
         - existing publishers are updated
         - deleted publishers are left untouched
        '''

        context = {'model': model,
                   'session': model.Session,
                   'user': self.user_name}

        organization_list_context = context.copy()
        organization_list_context['with_datasets'] = True
        existing_organizations = plugins.toolkit.get_action('organization_list')(
            organization_list_context, {'all_fields': True})

        existing_organizations = dict((g['name'], g) for g in existing_organizations)

        publishers = self._read_publishers_from_file(file_path)

        new_publishers = [p for p in publishers
                          if p.name not in existing_organizations]

        existing_publishers = [p for p in publishers
                               if p.name in existing_organizations]

        deleted_publishers = [
            organization_name for organization_name in existing_organizations.keys()
            if organization_name not in set(p.name for p in publishers)]

        self._add_publishers(new_publishers)

        # Update existing publishers
        organizations_title_lookup = {}
        for publisher in existing_publishers:
            context = {'model': model,
                       'session': model.Session,
                       'user': self.user_name,
                       'prevent_packages_update': True}
            if publisher.lang_code != 'en':
                continue
            existing_organization = existing_organizations[publisher.name]
            if existing_organization['title'] != publisher.title:
                # Update the organization
                log.info('Publisher required update: %s, [%s].  (Was: %s)',
                         publisher.title,
                         publisher.name,
                         existing_organization['title'])
                organization = existing_organization.copy()
                organization.update(title=publisher.title)

                # Remove some key value pairs to have a valid organization object passed to the
                # 'organization_update' action, not removing them would cause the action to fail
                #
                # 'organization_update' awaits a different data type (list of dicts) for 'packages'
                # than the call to 'organization_list' (with: {'all_fields': True}) has put here (int)
                organization.pop('packages', None)
                # display_name is not a valid property for 'organization_update'
                organization.pop('display_name', None)

                plugins.toolkit.get_action('organization_update')(context, organization)
            # Track the organization titles
            organizations_title_lookup[publisher.name] = \
                publisher.title or publisher.name

        # Update translations.
        self._update_translations(existing_publishers, organizations_title_lookup)

        # Just log which publishers should be deleted.
        for organization_name in deleted_publishers:
            organization = existing_organizations[organization_name]
            if organization['packages'] == 0:
                log.info('Deleting old organization %s as it has no datasets.',
                         organization['name'])
                context = {'model': model,
                           'session': model.Session,
                           'user': self.user_name}
                ckan.logic.get_action('organization_delete')(
                    context, organization)

            else:
                log.warn('Not deleting old publisher: %s because '
                         'it has datasets associated with it.',
                         organization_name)

    def _update_translations(self, publishers, organizations_title_lookup):
        translations = []
        for publisher in publishers:
            context = {'model': model,
                   'session': model.Session,
                   'user': self.user_name}
            if publisher.lang_code == 'en':
                continue
            if not publisher.title:
                continue

            if publisher.name not in organizations_title_lookup:
                log.warn('No english version of %s [%s].  Skipping',
                         publisher.title, publisher.name)
                continue

            translations.append({
                'term': organizations_title_lookup[publisher.name],
                'term_translation': publisher.title,
                'lang_code': publisher.lang_code
            })

        if translations:
            plugins.toolkit.get_action('legacy_term_translation_update_many')(
                context, {'data': translations}
            )

    def _create_vocab(self, context, vocab_name):
        try:
            log.info('Creating vocabulary "%s"' % vocab_name)
            vocab = plugins.toolkit.get_action('vocabulary_create')(
                context, {'name': vocab_name}
            )
        except logic.ValidationError, ve:
            # ignore errors about the vocab already existing
            # if it's a different error, reraise
            if not 'name is already in use' in str(ve.error_dict):
                raise ve
            log.info('Vocabulary "%s" already exists' % vocab_name)
            vocab = plugins.toolkit.get_action('vocabulary_show')(
                context, {'id': vocab_name}
            )
        return vocab

    def _delete_vocab(self, vocab_name):
        log.info('Deleting vocabulary "{0}"'.format(vocab_name))

        context = {'model': model,
                   'session': model.Session,
                   'user': self.user_name}

        try:
            vocab = plugins.toolkit.get_action('vocabulary_show')(
                context, {'id': vocab_name})
        except plugins.toolkit.ObjectNotFound:
                log.info('Vocab "{0}" not found, ignoring'.format(vocab_name))
                return

        for tag in vocab.get('tags'):
            log.info('Deleting tag "%s"' % tag['name'])
            plugins.toolkit.get_action('tag_delete')(
                context, {'id': tag['id']})
        plugins.toolkit.get_action('vocabulary_delete')(
            context, {'id': vocab['id']})

    def update_vocab_from_file(self, vocab_name, file_path=None):
        '''
        Create vocabularies and vocabulary tags using JSON files.
        If the vocabulary already exists, or the tag is already part
        of the vocab, it will be ignored.
        '''
        if not file_path:
            file_path = self.default_file[vocab_name]
        if not os.path.exists(file_path):
            log.error('File {0} does not exist'.format(file_path))
            sys.exit(1)

        context = {'model': model, 'session': model.Session,
                   'user': self.user_name}
        vocab = self._create_vocab(context, vocab_name)

        with open(file_path) as json_file:
            full_json = json.loads(json_file.read())

        translations = []
        tag_schema = ckan.logic.schema.default_create_tag_schema()
        tag_schema['name'] = [unicode]

        existing_tags = plugins.toolkit.get_action('tag_list')(
            context, {'vocabulary_id': vocab['id']})
        updated_tags = []

        for item in full_json['results']['bindings']:
            if item['language']['value'] == 'en':
                context = {'model': model,
                           'session': model.Session,
                           'user': self.user_name,
                           'schema': tag_schema}

                if (item['label']['value'] == 'Multilingual Code' and
                        vocab_name == forms.LANGUAGE_VOCAB_NAME):
                    continue

                term = item['term']['value']

                if not term in existing_tags:
                    log.info('Creating tag "{0}"'.format(term))
                    tag = {'name': term,
                           'vocabulary_id': vocab['id']}
                    plugins.toolkit.get_action('tag_create')(context, tag)

                updated_tags.append(term)

        for item in full_json['results']['bindings']:
            term = item['term']['value']
            translation = item['label']['value']
            if (translation == 'Multilingual Code' and
                    vocab_name == forms.LANGUAGE_VOCAB_NAME):
                continue
            if not translation:
                continue

            translations.append({'term': term,
                                 'term_translation': translation,
                                 'lang_code': item['language']['value']})

        plugins.toolkit.get_action('legacy_term_translation_update_many')(
            context, {'data': translations})

        # remove deleted tags
        # TODO: can we also remove translations of deleted tags?
        tags_to_delete = [t for t in existing_tags if not t in updated_tags]
        for tag_name in tags_to_delete:
            log.info('Deleting tag "{0}"'.format(tag_name))
            tag = {'id': tag_name,
                   'vocabulary_id': vocab['id']}
            plugins.toolkit.get_action('tag_delete')(context, tag)

    def _lookup_term(self, en_translation):
        '''
        Lookup existing term in term_translation table that has the given
        English translation. If none found, return the English translation.
        '''
        engine = model.meta.engine
        sql = '''
            SELECT term FROM term_translation
            WHERE term_translation=%s
            AND lang_code='en';
        '''
        result = engine.execute(sql, en_translation).fetchone()
        if not result:
            return en_translation
        else:
            return result[0]

    def import_csv_translation(self):
        self.import_csv_translations('odp-vocabulary-translate.csv')

    def import_csv_translation_licence(self):
        self.import_csv_translations('odp-vocabulary-translate-licence.csv')

    def import_csv_translations(self, odp_file_name):
        file_name = os.path.dirname(os.path.abspath(__file__)) + \
            '/../../data/' + odp_file_name
        voc_translate = file(file_name)
        voc_dicts = csv.DictReader(voc_translate)
        translations = []

        for line in voc_dicts:
            term = line.pop('en')
            for key in line:
                translations.append(
                    {'term': self._lookup_term(term),
                     'lang_code': key,
                     'term_translation': line[key].decode('utf8')})

        context = {'model': model, 'session': model.Session,
                   'user': self.user_name, 'extras_as_string': True}

        plugins.toolkit.get_action('legacy_term_translation_update_many')(
            context, {'data': translations}
        )


    def update_all_vocabs(self):
        self.update_vocab_from_file(forms.GEO_VOCAB_NAME)
        self.update_vocab_from_file(forms.DATASET_TYPE_VOCAB_NAME)
        self.update_vocab_from_file(forms.LANGUAGE_VOCAB_NAME)
        self.update_vocab_from_file(forms.STATUS_VOCAB_NAME)
        self.update_vocab_from_file(forms.INTEROP_VOCAB_NAME)
        self.update_vocab_from_file(forms.TEMPORAL_VOCAB_NAME)
        self.update_vocab_from_file(forms.EUROVOC_CONCEPTS_VOCAB_NAME)
        self.update_vocab_from_file(forms.EUROVOC_DOMAINS_VOCAB_NAME)
        self.import_csv_translation()
        self.import_csv_licence_translation()

    def delete_all_vocabs(self):
        self._delete_vocab(forms.GEO_VOCAB_NAME)
        self._delete_vocab(forms.DATASET_TYPE_VOCAB_NAME)
        self._delete_vocab(forms.LANGUAGE_VOCAB_NAME)
        self._delete_vocab(forms.STATUS_VOCAB_NAME)
        self._delete_vocab(forms.INTEROP_VOCAB_NAME)
        self._delete_vocab(forms.TEMPORAL_VOCAB_NAME)
        self._delete_vocab(forms.EUROVOC_CONCEPTS_VOCAB_NAME)
        self._delete_vocab(forms.EUROVOC_DOMAINS_VOCAB_NAME)

    def purge_publisher_datasets(self, publisher_name):
        context = {'model': model, 'session': model.Session,
                   'user': self.user_name}
        log.warn(plugins.toolkit.get_action('purge_publisher_datasets')(
            context, {'name': publisher_name}))

    def purge_package_extra_revision(self):
        context = {'model': model, 'session': model.Session,
                   'user': self.user_name}
        log.warn(plugins.toolkit.get_action('purge_package_extra_revision')(
            context, {}))

    def purge_task_data(self):
        context = {'model': model, 'session': model.Session,
                   'user': self.user_name}
        log.warn(plugins.toolkit.get_action('purge_task_data')(context, {}))

    def searchcloud_generate_unapproved_search_list(self):
        '''
        This command is usually executed via a Cron job once a week to
        replace the data in the search_popular_latest table
        '''
        searchcloud.generate_unapproved_list(model.Session, days=30)
        model.Session.commit()

    def searchcloud_install_tables(self):
        def out(text):
            print text
        searchcloud.install_tables(model.Session, out)
        model.Session.commit()
