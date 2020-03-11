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

import ckan.logic as logic
from ckanext.ecportal.lib import ui_util
from pylons import config
from ckanext.ecportal.lib.ui_util import _get_translated_term_from_dcat_object
from ckanext.ecportal.model.schemas.dcatapop_revision_schema import RevisionSchemaDcatApOp
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
import logging
DEFAULT_LANGUAGE = config.get('ckan.locale_default', 'en')

log = logging.getLogger(__name__)

_check_access = logic.check_access
NotFound = logic.NotFound

uri_prefix = config.get('ckan.ecodp.uri_prefix', '')


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    Based on the work of https://github.com/hughdbrown/dictdiffer
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):

        list_changed = []
        for o in self.intersect:
            past = self.past_dict[o]
            current = self.current_dict[o]
            if past != current:
                if isinstance(past, list) and isinstance(current,list):
                    if sorted(past) != sorted(current):
                        list_changed.append(o)
                else:
                    list_changed.append(o)

        return list_changed

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])
    def compile_diff(self):
        list_compiled = self.added()
        list_compiled.update(self.removed())
        list_compiled.update(self.changed())
        all_differences ={}
        for key in list_compiled:
            report = {'past':self.past_dict.get(key,''),'current':self.current_dict.get(key, '')}
            all_differences[key]=report
        return all_differences


def package_revision_list(context, data_dict):
    """
    Return a dataset (package)'s revisions as a list of dictionaries.
    :param context:
    :param data_dict:
    :return:
    """
    pkg = context.get('package')  # type: DatasetDcatApOp
    if pkg is None:
        raise NotFound

    _check_access('package_revision_list', context, data_dict)

    revision_dicts = []
    list_revisions_from_ts = pkg.get_list_revisions()


    for revision in list_revisions_from_ts.values():
        revision_dict = {}
        rev = revision.get('revision')  # type : RevisionSchemaDcatApOp
        revision_dict["id"] = rev.uri.split('/')[-1]
        revision_dict["timestamp"] = rev.timestamp_revision.get('0').value_or_uri
        revision_dict["author"] = rev.author_revision.get('0').value_or_uri
        revision_dict["message"] = "msg"  # todo: add the message
        revision_dicts.append(revision_dict)

    return sorted(revision_dicts, key=lambda k: k["timestamp"], reverse=True)


def diff_datasets(context, data_dict, id_revision_to, id_revision_from):
    '''
    create the list of difference between the two revisions
    :param context:
    :param data_dict:
    :param id_revision_to:
    :param id_revision_from:
    :return:
    '''

    model = context["model"]
    dataset = context.get('package')  # type: DatasetDcatApOp
    if dataset is None:
        raise NotFound

    _check_access('package_revision_list', context, data_dict)

    try:
        diff_dict = {}
        diff_report = {}
        list_revisions_from_ts = data_dict.get('list_revisions', None)
        if list_revisions_from_ts:
            uri_new_dataset = '{0}/revision/{1}'.format(uri_prefix, id_revision_to)
            uri_old_dataset = '{0}/revision/{1}'.format(uri_prefix, id_revision_from)
            dataset_new_obj = next((rev for rev in list_revisions_from_ts if rev.get('revision').uri == uri_new_dataset),None)
            dataset_old_obj = next((rev for rev in list_revisions_from_ts if rev.get('revision').uri == uri_old_dataset),None)
            dataset_new = dataset_new_obj.get('dataset', None)
            dataset_old = dataset_old_obj.get('dataset', None)
            revision_to = dataset_new_obj.get('revision', None)  # type:RevisionSchemaDcatApOp
            revision_from = dataset_old_obj.get('revision',  None)  # type: RevisionSchemaDcatApOp
            if dataset_new and dataset_old:

                dict_dataset_new = ui_util.transform_dcat_schema_to_form_schema(dataset_new)
                dict_dataset_old = ui_util.transform_dcat_schema_to_form_schema(dataset_old)

                differ = DictDiffer(dict_dataset_new,dict_dataset_old)
                all_differences = differ.compile_diff() #type: dict
                diff_report['revision_to_time'] = revision_to.timestamp_revision.get('0', '').value_or_uri
                diff_report['revision_from_time'] = revision_from.timestamp_revision.get('0', '').value_or_uri

                diff_report['title'] = _get_translated_term_from_dcat_object(dataset.schema, 'title_dcterms',
                                                                             DEFAULT_LANGUAGE)
                diff_report['diff_dict'] = all_differences.items()
                return diff_report

            else:
                log.error('Revision: Difference can not find revisions')
                raise NotFound
        else:
            raise NotFound("Revisons not found for dataset {0}".pkg.datset_uri)
    except basestring as e:
        log.error(e)
