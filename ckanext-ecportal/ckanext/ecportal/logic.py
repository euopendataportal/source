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

import ckan.lib.navl.dictization_functions
import logging
import urlparse
import hashlib
import numbers

from pylons import config
import ckan.lib.dictization as d
import ckan.lib.navl.dictization_functions as dict_func
import ckan.logic as logic
import ckan.model as ckan_model
import ckanext.ecportal.helpers as helpers
import ckanext.ecportal.multilingual.plugin as multilingual_plugin
import ckanext.ecportal.schema as schema
import ckanext.ecportal.unicode_sort as unicode_sort
import ujson as json
import cPickle as pickle
import ckanext.ecportal.lib.cache.redis_cache as redis_cache



UNICODE_SORT = unicode_sort.UNICODE_SORT
_RESOURCE_MAPPING = None
NotFound = logic.NotFound

_validate = ckan.lib.navl.dictization_functions.validate

log = logging.getLogger(__name__)

def _get_filename_and_extension(resource):
    url = resource.get('url').rstrip('/')
    if '?' in url:
        return '', ''
    if 'URL' in url:
        return '', ''
    url = urlparse.urlparse(url).path
    split = url.split('/')
    last_part = split[-1]
    ending = last_part.split('.')[-1].lower()
    if len(ending) in [2, 3, 4] and len(last_part) > 4 and len(split) > 1:
        return last_part, ending
    return '', ''


def sort_organization(key):
    if isinstance(key, basestring):
        display_name = key
    else:
        display_name = key.get('display_name', '')
    # Strip accents first and if equivilant do next stage comparison.
    # Leaving space and concatenating is to avoid having todo a real
    # 2 level sort.
    return (unicode_sort.strip_accents(display_name) +
            '   ' +
            display_name).translate(UNICODE_SORT)


def organization_list(context, data_dict):
    '''Return a list of the names of the site's organization.

    :param order_by: the field to sort the list by, must be ``'name'`` or
      ``'packages'`` (optional, default: ``'name'``) Deprecated use sort.
    :type order_by: string
    :param sort: sorting of the search results.  Optional.  Default:
        "name asc" string of field name and sort-order. The allowed fields are
        'name' and 'packages'
    :type sort: string
    :param groups: a list of names of the groups to return, if given only
        groups whose names are in this list will be returned (optional)
    :type groups: list of strings
    :param all_fields: return full group dictionaries instead of  just names
        (optional, default: ``False``)
    :type all_fields: boolean

    :rtype: list of strings
    '''

    key = json.dumps(data_dict)
    active_cache = config.get('ckan.cache.active', 'false')
    organizations = None
    if active_cache == 'true':
        organization_str = redis_cache.get_from_cache(key, pool=redis_cache.MISC_POOL)
        if organization_str:
            organizations = pickle.loads(organization_str)
        else:
            organizations = logic.action.get.organization_list(context, data_dict)
            redis_cache.set_value_no_ttl_in_cache(key,pickle.dumps(organizations), pool=redis_cache.MISC_POOL)

    if context.get('for_view', False):
        # in the web UI only list publishers with published datasets

        # depending upon the context, group['packages'] may be either a
        # count of the packages, or the actual list of packages
        if organizations and isinstance(organizations[0]['packages'], int):
            organizations = [g for g in organizations if g['packages'] > 0]
        else:
            organizations = [g for g in organizations if len(g['packages']) > 0]

    return organizations if 'sort' in data_dict.keys() else sorted(organizations, key=sort_organization)


def _change_resource_details(resource):
    formats = helpers.resource_mapping().keys()
    resource_format = resource.get('format', '').lower().lstrip('.')
    filename, extension = _get_filename_and_extension(resource)
    if not resource_format:
        resource_format = extension
    if resource_format in formats:
        resource['format'] = helpers.resource_mapping()[resource_format][0]
        if resource.get('name', '') in ['Unnamed resource', '', None] and resource.get('description', '') in ['', None]:
            resource['name'] = helpers.resource_mapping()[resource_format][2]
    elif resource.get('name', '') in ['Unnamed resource', '', None] and resource.get('description', '') in ['', None]:
        if extension and not resource_format:
            if extension in formats:
                resource['format'] = helpers.resource_mapping()[extension][0]
            else:
                resource['format'] = extension.upper()
        resource['name'] = 'Web Page'

    if filename and not resource.get('description'):
        resource['description'] = filename


def package_show_unaltered(context, data_dict):
    '''Return the metadata of a dataset (package) and its resources.

    :param id: the id or name of the dataset
    :type id: string

    :rtype: dictionary

    '''
    # Override package_show to sort the resources by name
    result = logic.action.get.package_show(context, data_dict)

    def order_key(resource):
        return resource.get('name', resource.get('description', ''))

    if 'resources' in result:
        result['resources'].sort(key=order_key)

    return result

def package_show(context, data_dict):
    '''Return the metadata of a dataset (package) and its resources.

    :param id: the id or name of the dataset
    :type id: string

    :rtype: dictionary

    '''
    # Override package_show to sort the resources by name
    result = package_show_unaltered(context, data_dict)

    for resource in result.get('resources', None):
        _change_resource_details(resource)

    return result

def resource_show(context, data_dict):
    resource = logic.action.get.resource_show(context, data_dict)
    _change_resource_details(resource)
    # translates the resources like the dataset
    resource = multilingual_plugin.translate_data_dict_for_resource(resource)
    return resource


def purge_publisher_datasets(context, data_dict):
    """
    Purge all deleted datasets belonging to a given publisher.

    :returns: Info about the command's result
    :rtype: dictionary
    """

    def do_purge(dataset_ids):
        model.repo.new_revision()
        # Every single purge is a rather heavy operation
        for ds_id in dataset_ids:
            dataset = model.Package.get(ds_id)
            dataset.purge()
        model.repo.commit_and_remove()

    logic.check_access('purge_publisher_datasets', context, data_dict)

    model = context['model']
    engine = model.meta.engine

    publisher_name = logic.get_or_bust(data_dict, 'name')
    group = model.Group.get(publisher_name)
    if not group:
        error_text = "Publisher '{0}' not found; please specify an existing publisher".format(publisher_name)
        raise logic.NotFound(error_text)

    deleted_datasets = '''
        SELECT DISTINCT package.id
        FROM package
            INNER JOIN member ON (member.table_name='package' AND member.table_id=package.id)
            INNER JOIN "group" ON ("group".id=member.group_id)
        WHERE "group".name='{publisher_name}' AND package.state='deleted';
        '''.format(publisher_name=publisher_name)

    try:
        db_rows = engine.execute(deleted_datasets)
        datasets_to_delete = [elent[0] for elent in db_rows] # list comprehension
        #datasets_to_delete = map(lambda elent : elent[0], db_rows) # lambda
        num_datasets_to_delete = len(datasets_to_delete)
    except Exception, e:
        raise logic.ActionError('Error executing sql: %s' % e)

    PURGE_COUNT_PER_TRANS = 100
    num_datasets_deleted = 0
    result_msg = 'nothing to purge'

    if num_datasets_to_delete > 0:
        log.info("Start to purge {0} datasets of publisher '{1}'. This may take some time..."
                 .format(num_datasets_to_delete, publisher_name))

    while datasets_to_delete:
        # do kind of a "multiple pop" (no slicing error if index is higher as nr. of elements!)
        sublist_to_delete = datasets_to_delete[:PURGE_COUNT_PER_TRANS]
        del datasets_to_delete[:PURGE_COUNT_PER_TRANS]

        do_purge(sublist_to_delete)
        num_datasets_deleted += len(sublist_to_delete)

        result_msg = "{0} of {1}".format(num_datasets_deleted, num_datasets_to_delete)
        log.info("Purged '{0}' datasets: {1}".format(publisher_name, result_msg))

    return {'publisher_datasets_purged': result_msg}


def purge_revision_history(context, data_dict):
    '''
    Purge a given publisher's unused revision history.

    :param group: the name or id of the publisher
    :type group: string

    :returns: number of resources and revisions purged.
    :rtype: dictionary
    '''
    logic.check_access('purge_revision_history', context, data_dict)

    model = context['model']
    engine = model.meta.engine
    group_id = logic.get_or_bust(data_dict, 'group')
    group = model.Group.get(group_id)

    if not group:
        raise logic.NotFound('Publisher {0} not found'.format(group_id))

    RESOURCE_IDS_SQL = '''
        SELECT resource.id FROM resource
        JOIN resource_group ON resource.resource_group_id = resource_group.id
        JOIN member ON member.table_id = resource_group.package_id
        JOIN "group" ON "group".id = member.group_id
        WHERE "group".name      = %s
          AND "group".type      = 'organization'
          AND member.table_name = 'package'
          AND resource.state    = 'deleted'
    '''

    DELETE_REVISIONS_SQL = '''
        DELETE FROM resource_revision
            WHERE id IN ({sql})
    '''.format(sql=RESOURCE_IDS_SQL)

    # Not necessary to use a sub-select, but it allows re-use of sql statement
    # and this isn't performance critical code.
    DELETE_RESOURCES_SQL = '''
        DELETE FROM resource WHERE id IN ({sql})
    '''.format(sql=RESOURCE_IDS_SQL)

    try:
        number_revisions_deleted = engine.execute(
            DELETE_REVISIONS_SQL,
            group.name
        ).rowcount

        number_resources_deleted = engine.execute(
            DELETE_RESOURCES_SQL,
            group.name
        ).rowcount

    except Exception, e:
        raise logic.ActionError('Error executing sql: %s' % e)

    return {'number_revisions_deleted': number_revisions_deleted,
            'number_resources_deleted': number_resources_deleted}


def purge_package_extra_revision(context, data_dict):
    '''
    Purge old data from the package_extra_revision table.

    :returns: number of revisions purged.
    :rtype: dictionary
    '''
    logic.check_access('purge_package_extra_revision', context, data_dict)

    model = context['model']
    engine = model.meta.engine

    delete_old_extra_revisions = '''
        DELETE FROM package_extra_revision WHERE current=false;
    '''

    try:
        revision_rows_deleted = engine.execute(
            delete_old_extra_revisions).rowcount

    except Exception, e:
        raise logic.ActionError('Error executing sql: %s' % e)

    return {'revision_rows_deleted': revision_rows_deleted}


def purge_task_data(context, data_dict):
    '''
    Purge data from the task_status and kombu_message tables
    (used by CKAN tasks and Celery).

    To just clear the Celery data (and not the task_status table),
    see the 'celery clean' command in CKAN core.

    :returns: number of task_status and Celery (kombu_message) rows deleted.
    :rtype: dictionary
    '''
    logic.check_access('purge_task_data', context, data_dict)

    model = context['model']
    engine = model.meta.engine

    purge_task_status = 'DELETE FROM task_status;'
    purge_celery_data = 'DELETE FROM kombu_message;'

    try:
        task_status_rows_deleted = engine.execute(purge_task_status).rowcount
        celery_rows_deleted = engine.execute(purge_celery_data).rowcount

    except Exception, e:
        raise logic.ActionError('Error executing sql: %s' % e)

    return {'task_status_rows_deleted': task_status_rows_deleted,
            'celery_rows_deleted': celery_rows_deleted}


def user_create(context, data_dict):
    '''Create a new user.

    You must be authorized to create users.

    Wrapper around core user_create action ensures that the ECODP custom user
    schema are used.

    :param name: the name of the new user, a string between 2 and 100
        characters in length, containing only alphanumeric characters, ``-``
        and ``_``
    :type name: string
    :param email: the email address for the new user (optional)
    :type email: string
    :param password: the password of the new user, a string of at least 4
        characters
    :type password: string
    :param id: the id of the new user (optional)
    :type id: string
    :param fullname: the full name of the new user (optional)
    :type fullname: string
    :param about: a description of the new user (optional)
    :type about: string
    :param openid: (optional)
    :type openid: string

    :returns: the newly created user
    :rtype: dictionary
    '''
    new_context = context.copy()  # Don't modify caller's context
    user_schema = context.get('schema', logic.schema.default_user_schema())
    new_context['schema'] = schema.default_user_schema(user_schema)
    return logic.action.create.user_create(new_context, data_dict)


def user_update(context, data_dict):
    '''Update a user account.

    Normal users can only update their own user accounts. Sysadmins can update
    any user account.

    For further parameters see ``user_create()``.

    :param id: the name or id of the user to update
    :type id: string

    :returns: the updated user account
    :rtype: dictionary

    '''
    new_context = context.copy()  # Don't modify caller's context
    user_schema = context.get('schema',
                              logic.schema.default_update_user_schema())
    new_context['schema'] = schema.default_update_user_schema(user_schema)
    return logic.action.update.user_update(new_context, data_dict)

def vocabulary_show_without_package_detail(context, data_dict):
    '''Return a single tag vocabulary without package details.

    :param id: the id or name of the vocabulary
    :type id: string
    :return: the vocabulary.
    :rtype: dictionary

    '''

    vocab_id = data_dict.get('id')
    if not vocab_id:
        raise logic.ValidationError({'id': 'id not in data'})
    vocabulary = ckan_model.vocabulary.Vocabulary.get(vocab_id)
    if vocabulary is None:
        raise NotFound(_('Could not find vocabulary "%s"') % vocab_id)
    vocabulary_dict = d.table_dictize(vocabulary, context)
    assert not vocabulary_dict.has_key('tags')
    vocabulary_dict['tag_count'] = vocabulary.tags.count()
    vocabulary_dict['tags'] = [tag_dictize_without_package_detail(tag, context) for tag
            in vocabulary.tags]
    tags = vocabulary_dict['tags']
    tagsorted = sorted(tags, key=lambda k:k['package_count'], reverse=True)
    vocabulary_dict['tags'] = tagsorted
    return vocabulary_dict

def tag_dictize_without_package_detail(tag, context):
    result_dict = d.table_dictize(tag, context)
    result_dict["package_count"] = len(tag.packages)
    result_dict["icon"] = ""
    return result_dict

def domain_list(context, data_dict):
    logic.check_access('group_list', context, data_dict)
    return _domain_or_group_list(context, data_dict, "eurovoc_domain")

def group_list(context, data_dict):
    logic.check_access('group_list', context, data_dict)
    return _domain_or_group_list(context, data_dict, "group")

def _domain_or_group_list(context, data_dict, type):
    data_dict["all_fields"]=True
    result = logic.action.get.group_list(context, data_dict)
    filtered_return = filter(lambda group: group['type'] == type, result)
    return filtered_return

def next_group_list(context, data_dict):
    all_groups = group_list(context, data_dict)
    i = data_dict["set_number"]
    amount = data_dict["set_amount"]

    if all_groups is None:
        return {"hasmore":False, "groups":None}
    else :
        groups = all_groups[(i-1)*amount : (i*amount)]
        result = {"hasmore":(len(all_groups)> (i*amount)),"groups":groups}
        return result

def skos_hierarchy_update(context, data_dict):
    '''
    Truncate organization hierarchy table and fill it again.
    '''
    model = context['model']


    #logic.check_access('member_create', context, data_dict)

    q_group = ckan_model.Session.query(ckan_model.Group)

    try:
        q = ckan_model.Session.query(ckan_model.Member)\
        .filter(ckan_model.Member.table_name == 'group')\
        .filter(ckan_model.Member.state == 'active')

        for member in q.all():
            member_dict = {
                'id': member.group_id,
                'object': member.table_id,
                'object_type': 'group',
                'capacity': 'public',
                }
            ckan.logic.get_action('member_delete')(context, member_dict)

        #engine.execute(delete_org_parent)
        #row_counts_int = engine.execute(row_count).cursor.rownumber


        if len(q.all()) > 0:
            raise logic.ActionError('Not all elements has been deleted')

        #all_groups = engine.execute(groups_rows).fetchall()
        all_groups = q_group.all()

        full_list = data_dict.get('results', {}).get('bindings', [])
        for current_elem in full_list:
            cb_value = current_elem.get('cb_name', {}).get('value', None)
            p_value = current_elem.get('p_name', {}).get('value', None)
            p_group = None
            cb_group = None

            if cb_value is not None:
                q_cb = ckan_model.Session.query(ckan_model.Group)\
                    .filter(ckan_model.Group.name == cb_value.lower())
                cb_group_fetch = q_cb.all()
                if len(cb_group_fetch)>0:
                    cb_group = cb_group_fetch[0]


            if p_value is not None:
                q_p = ckan_model.Session.query(ckan_model.Group)\
                    .filter(ckan_model.Group.name == p_value.lower())
                p_group_fetch = q_p.all()
                if len(p_group_fetch)>0:
                    p_group = p_group_fetch[0]


            is_addable = True

            if cb_group not in all_groups:
                log.error('The group %s does not exists in the list of the groups' % cb_value)
                is_addable = False


            if p_group is None:
                log.error('The group %s has no child' % p_value)
                is_addable = False
            elif p_group not in all_groups:
                log.error('The group %s does not exists in the list of the groups' % p_value)
                is_addable = False





            if is_addable:
                #key = hashlib.md5(cb_value).hexdigest()
                #key = "'" + key + "'"

                #INSERT_ORG_TABLE = '''
                #INSERT INTO org_parent VALUES ({key}, {org_name}, {org_parent_name})
                #'''.format(key=key, org_name=cb_value,
                #           org_parent_name=p_value)

                if cb_group is not None:
                    cb_val = cb_group.id
                else:
                    cb_val = None

                if p_group is not None:
                    p_val = p_group.id
                else:
                    p_val = None

                member_dict = {
                    'object': cb_val,
                    'id': p_val,
                    'object_type': 'group',
                    'capacity': 'public',
                }



                logic.get_action('member_create')(context, member_dict)

    except Exception, e:
        log.error('Error during process skos_hierarchy_update: %s' % e)

def transform_to_data_dict(reqest_post):
    '''
    Transform the POST body to data_dict usable by the actions ('package_update', 'package_create', ...)
    :param the POST body of the request object
    :return: a dict usable by the actions
    '''

    # Initialize params dictionary
    data_dict = logic.parse_params(reqest_post)

    for key in data_dict.keys():
        if 'template' in key:
            data_dict.pop(key, None)
        # if 'extras' in key and data_dict[key] == '':
        #     data_dict.pop(key)

    # Transform keys like 'group__0__key' to a tuple (like resources, extra fields, ...)
    try:
        data_dict.pop('file', None)
        data_dict = tuplize_dict(data_dict)
    except Exception, e:
        log.error(e.message)

    # Collect all tuplized key groups in one key containing a list of dicts
    data_dict = dict_func.unflatten(data_dict)
    for items in data_dict.get('dataset', {}):
        items['extras'] = convert_dit2list(items.get('extras', {}))
        items['resources_documentation'] = convert_dit2list(items.get('resources_documentation', {}))
        items['resources_visualization'] = convert_dit2list(items.get('resources_visualization', {}))
        items['resources_distribution'] = convert_dit2list(items.get('resources_distribution', {}))
    data_dict = logic.clean_dict(data_dict)

    return data_dict

def tuplize_dict(data_dict):
    '''Takes a dict with keys of the form 'table__0__key' and converts them
    to a tuple like ('table', 0, 'key').

    Dict should be put through parse_dict before this function, to have
    values standardized.

    May raise a DataError if the format of the key is incorrect.
    '''
    tuplized_dict = {}
    for key, value in data_dict.iteritems():
        key_list = key.split('__')
        for num, key in enumerate(key_list):
            if num % 2 == 1:
                try:
                    key_list[num] = int(key)
                except ValueError:
                    raise dict_func.DataError('Bad key')
        tuplized_dict[tuple(key_list)] = value
    return tuplized_dict



def convert_dit2list(data_dict):

    data_list = []

    for key, value in data_dict.iteritems():

        if isinstance(key, numbers.Number):
            data_list.append(value)


    return data_list

