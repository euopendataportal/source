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
import os
import traceback

import ckan.logic as logic
import ckanext.ecportal.lib.validation.validation_json_converter as converter

from ckanext.ecportal.model.schema_validation.validation_type_result import ValidationTypeResult
from ckan.common import _
from ckanext.ecportal.model.dataset_dcatapop import DatasetDcatApOp
from ckanext.ecportal.lib.ui_util import _get_doi_from_adms_identifier, _count_doi_from_adms_identifier, _get_other_identifier_from_adms_identifier
from ckanext.ecportal.virtuoso.utils_triplestore_query_helpers import TripleStoreQueryHelpers
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil

log = logging.getLogger(__name__)
default_data_dir = os.path.dirname(os.path.abspath(__file__))
_check_access = logic.check_access
ValidationError = logic.ValidationError

FATAL_RULES = default_data_dir + '/../../../data/dataset_fatal_rules.json'
ERROR_RULES = default_data_dir + '/../../../data/dataset_error_rules.json'
WARNING_RULES = default_data_dir + '/../../../data/dataset_warning_rules.json'


def __provide_validation_rules():
    rules = {'fatal': {},
             'error': {},
             'warning': {}
             }
    decoder = converter.WheezyJSONDecoder()

    with open(FATAL_RULES) as data_file:
        try:
            rules['fatal'] = decoder.decode(data_file.read())
        except TypeError, e:
            log.error(str(e))
            log.error(traceback.print_exc())
    data_file.close()

    with open(ERROR_RULES) as data_file:
        try:
            rules['error'] = decoder.decode(data_file.read())
        except TypeError, e:
            log.error(str(e))
            log.error(traceback.print_exc())
    data_file.close()

    with open(WARNING_RULES) as data_file:
        try:
            rules['warning'] = decoder.decode(data_file.read())
        except TypeError, e:
            log.error(str(e))
            log.error(traceback.print_exc())
    data_file.close()
    return rules


def validate_dataset(context, data_dict):
    dataset = None  # type: DatasetDcatApOp
    if data_dict.get('rdf'):
        pass

    elif data_dict.get('ttl'):
        pass
    else:  # old model, use migration
        pass

    dataset, errors = validate_dacat_dataset(dataset, context)

    if errors.get('fatal') or errors.get('error'):
        raise ValidationError(errors)

    return data_dict


def validate_dacat_dataset(dataset, context=None):
    '''

    :param dict context:
    :param DatasetDcatApOp|dict dataset:
    :return:
    '''
    import time
    start = time.time()
    context = context or {}
    assert isinstance(dataset, DatasetDcatApOp)

    final_validation_dataset_report = dataset.validate_dataset()
    dataset_class_uri = ["http://www.w3.org/ns/dcat#Dataset","http://www.w3.org/ns/dcat#CatalogRecord"]
    resource_class_uri = ["http://www.w3.org/ns/dcat#Distribution", "document", "http://xmlns.com/foaf/0.1/Document"]
    ui_validation_report = {ValidationTypeResult.fatal: {}, ValidationTypeResult.error: {},
                            ValidationTypeResult.warning: {}, ValidationTypeResult.success: {}}

    for error_level, list_validation_report_for_property in final_validation_dataset_report.iteritems():
        for validation_property_report in list_validation_report_for_property:
            # the case of dataset
            class_of_instance = validation_property_report.get('class')
            uri_instance = validation_property_report.get('uri_resource')
            name_rule = validation_property_report.get('name', "")
            message_rule = validation_property_report.get('message', "")
            property_to_validate = validation_property_report.get('property')

            if class_of_instance in dataset_class_uri:
                list_name_error = ui_validation_report[error_level].get(property_to_validate, [])
                list_name_error.append(_(message_rule))
                ui_validation_report[error_level][property_to_validate] = list_name_error
            if class_of_instance in resource_class_uri:
                list_validation_resource = ui_validation_report[error_level].get('resources', [])
                # find the dict of error for the resource
                resource_report = {'uri': uri_instance}
                # find the error dict of the instance
                existing_resource = False
                for res_report in list_validation_resource:
                    if res_report.get('uri', '') == uri_instance:
                        resource_report = res_report
                        existing_resource = True
                    break
                list_name_error = resource_report.get(property_to_validate, [])
                list_name_error.append(_(message_rule))
                resource_report[property_to_validate] = list_name_error
                if not existing_resource:
                    list_validation_resource.append(resource_report)
                ui_validation_report[error_level]['resources'] = list_validation_resource

    validate_identifier_adms(dataset, ui_validation_report)
    if context and context.get('old_dataset'):
        validate_doi(dataset, ui_validation_report, context.get('old_dataset'))
    duration = time.time() - start
    log.info("[Dataset] [validation] [succesfull] [dataset:<{0}>] [duration:{1}]".format(dataset.dataset_uri,duration))
    return dataset, ui_validation_report


def validate_identifier_adms(dataset, errors):
    from ckanext.ecportal.model.schemas.dcatapop_identifier_schema import IdentifierSchemaDcatApOp
    new_identifier_adms = dataset.schema.identifier_adms.values()
    for identifier in new_identifier_adms:
        if not isinstance(identifier, IdentifierSchemaDcatApOp):
            add_to_report(errors, 'fatal', 'identifier_adms', "ckan.dataset.identifier_type.invalid")
        else:
            # adms:identifier should have two skos:notation properties
            if len(identifier.notation_skos.values()) < 2:
                add_to_report(errors, 'error', 'identifier_adms', "ckan.dataset.identifier_type.notation_cardinallity")
                continue

            for notation in identifier.notation_skos.values():
                #  skos:notation properties should have a type
                if not notation.datatype:
                    add_to_report(errors, 'error', 'identifier_adms', "ckan.dataset.notation_type.invalid")
                    break
                #  skos:notation properties should be a value of controlled vocabulary
                if ControlledVocabularyFactory.NOTATION_TYPE not in notation.datatype and ControlledVocabularyFactory.DATACITE_NOTATION not in notation.datatype:
                    add_to_report(errors, 'error', 'identifier_adms', "ckan.dataset.notation_type.invalid")
                    break

def is_ckanName_unique(name):
    return TripleStoreQueryHelpers().is_ckanName_unique(name)


def is_DOI_unique(name):
    return TripleStoreQueryHelpers().is_DOI_unique(name)


def validate_doi(dataset, errors, old_dataset):
    new_identifier_adms = _get_doi_from_adms_identifier(dataset.schema.identifier_adms).value_or_uri
    old_identifier_adms = _get_doi_from_adms_identifier(old_dataset.identifier_adms).value_or_uri or None

    rollback = False
    if old_identifier_adms and not new_identifier_adms:
        add_to_report(errors, 'fatal', 'identifier_adms', "ckan.dataset.doi.invalid")
        rollback = True
    elif not old_identifier_adms and not new_identifier_adms:
        return

    if _count_doi_from_adms_identifier(old_dataset.identifier_adms) > 1 or _count_doi_from_adms_identifier(dataset.schema.identifier_adms) > 1:
        add_to_report(errors, 'fatal', 'identifier_adms', "ckan.dataset.doi.multiple")
        rollback = True
    else:

        if not old_identifier_adms:
            # Assume that we can add a new doi but it must be unique
            if new_identifier_adms and not is_DOI_unique(new_identifier_adms):
                add_to_report(errors, 'fatal', "identifier_adms", "ckan.dataset.doi.non_unique")
                rollback = True
        else:
            if new_identifier_adms and old_identifier_adms != new_identifier_adms:
                add_to_report(errors, 'fatal', "identifier_adms", "ckan.dataset.doi.invalid")
                rollback = True

    if rollback:
        dataset.schema.identifier_adms = old_dataset.identifier_adms


# err_type = fatal, error, warning
def add_to_report(report, err_type, err_key, atto_key):
    list_errors = report[err_type].get(err_key, [])
    list_errors.append(_(atto_key))
    report[err_type].update({err_key: list_errors})


def validate_parameter_package_save(parameter_dict):
    '''

    :param parameter_dict:
    :return:
    '''

    validation_structure_parameter = "parameter of package save must be a json"
    validation_addReplaces_not_found = "addReplaces is missing"
    validation_addReplaces_not_array = "No action found in addReplaces"
    validation_addReplace_json = "addReplace action must be a json"
    validation_objectUri_not_found = "objectUri is missing"
    validation_objectUri_incorrect = "Incorrect value of objectUri"
    validation_action_addReplace = "addReplace action action is not a dict"
    validation_addReplace_incorrect = "addReplace must be a json"
    validation_addReplace_not_found = "addReplace is missing"
    validation_objectStatus_not_found = "objectStatus is missing"
    validation_objectStatus_incorrect = "objectStatus value is incorrect"

    validation_rdfFile_not_found = "rdfFile is missing"
    validation_rdfFile_incorrect = "rdfFile value is incorrect"
    validation_not_authorized_parameter = "Not authorized parameter"
    report = {}
    validation = False
    if not isinstance(parameter_dict, dict):
        report["structure_parameter"] = validation_structure_parameter
        valide = False
        final_report = {"validation_json_structure": report}
        return final_report

    for key in parameter_dict:
        if key not in ["addReplaces","rdfFile"]:
            #
            # Relax this rule for 5.1
            # report[key] =validation_not_authorized_parameter
            pass

    rdf_file = parameter_dict.get("rdfFile", None)
    if rdf_file is None:
        report["rdfFile"] = validation_rdfFile_not_found
    else:
        if not isinstance(rdf_file, basestring) or len(rdf_file) == 0:
            report["rdfFile"] = validation_rdfFile_incorrect

    add_replaces = parameter_dict.get("addReplaces", None)
    if add_replaces is None:
        report["addReplaces"] = validation_addReplaces_not_found

    else:
        if not isinstance(add_replaces, list):
            report["addReplaces"] = validation_addReplaces_not_array
            final_report = {"validation_json_structure": report}
            return final_report

        if len(add_replaces) == 0:
            report["addReplaces"] = validation_addReplaces_not_array
        report_actions=[]
        order = 0
        for action_dict in add_replaces:
            str_action = str(action_dict)
            order = order+1
            report_action = {}
            # report_action = {"action_{0}".format(order):"{0}".format(str_action)}
            if not isinstance(action_dict, dict):
                report_action["addReplace"] = validation_action_addReplace
                action_dict= {}

            for key in action_dict:
                if key not in ["objectUri","addReplace"]:
                    # Relax this rule for 5.1
                    # report_action[key] = validation_not_authorized_parameter
                    pass

            object_uri = action_dict.get("objectUri", None)
            if not object_uri:
                report_action["objectUri"] = validation_objectUri_not_found
            else:
                if "http://data.europa.eu/88u/dataset" not in object_uri:
                    report_action["validation_objectUri"] = validation_objectUri_incorrect
            add_replace = action_dict.get("addReplace", None)
            if add_replace is None:
                report_action["addReplace"] = validation_addReplace_not_found
            else:
                if not isinstance(add_replace, dict):
                    report_action["addReplace"] = validation_addReplace_incorrect
                else:
                    object_status = add_replace.get("objectStatus", None)
                    if object_status is None:
                        report_action["objectStatus"] = validation_objectStatus_not_found
                    if not isinstance(object_status, basestring):
                        report_action["objectStatus"] = validation_objectStatus_not_found
            if report_action:
                report_actions.append(report_action)
                report['actions'] = report_actions
    final_report = {"validation_json_structure":report}
    return final_report
