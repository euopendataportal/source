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

import ckanext.ecportal.model.ecodp_resource_term_translation as ecodp_resource_term_translation
import ckan.model as model
import ckanext.ecportal.model as ckan_model
import pylons.config as config
from sqlalchemy import and_

log = logging.getLogger(__file__)


def resource_term_translation_create(context, dict):
    #Create multiple resources translations from package and translations dicts
    list_lang = dict['list_lang']
    data_dict = dict['data_dict']

    if list_lang:
        for resource in list_lang:
            for lang, translation in resource.iteritems():
                iteration = translation['iteration']
                res_trans_table = ecodp_resource_term_translation.resource_term_translation_table

                for key, value in translation.iteritems():
                    if 'lang' != key and 'iteration' != key:

                        result = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table)\
                        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == data_dict['resources'][iteration]['id'])\
                        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == data_dict['resources'][iteration]['revision_id'])\
                        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.field == key)\
                        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.lang_code == lang)\
                        .count()


                        if result>0:
                            update = res_trans_table.update().where(
                            and_(res_trans_table.c.resource_id == data_dict['resources'][iteration]['id'],
                                res_trans_table.c.resource_revision_id == data_dict['resources'][iteration]['revision_id'],
                            res_trans_table.c.field == key,
                            res_trans_table.c.lang_code == lang)).values(field_translation = translation[key])

                            conn = model.Session.connection()
                            conn.execute(update)
                        else:
                            insert = res_trans_table.insert()
                            insert = insert.values(lang_code = lang)
                            insert = insert.values(field = key)
                            insert = insert.values(field_translation = translation[key])
                            insert = insert.values(resource_id = data_dict['resources'][iteration]['id'])
                            insert = insert.values(resource_revision_id = data_dict['resources'][iteration]['revision_id'])

                            conn = model.Session.connection()
                            conn.execute(insert)




        model.Session.commit()


def resource_term_translation_create_multiple(context, dict):

    list = dict['resources']
    #Create multiple resources translations from list of resources translations
    for resource in list:
        for lang, translations in resource.iteritems():

            res_trans_table = ecodp_resource_term_translation.resource_term_translation_table

            for translation in translations:
                result = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table)\
                .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == translation['resource_id'])\
                .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == translation['resource_revision_id'])\
                .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.field == translation['field'])\
                .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.lang_code == translation['lang_code'])\
                .count()

                if result>0:
                    update = res_trans_table.update().where(
                    and_(res_trans_table.c.resource_id == translation['resource_id'],
                        res_trans_table.c.resource_revision_id == translation['resource_revision_id'],
                    res_trans_table.c.field == translation['field'],
                    res_trans_table.c.lang_code == lang)).values(field_translation = translation['field_translation'])

                    conn = model.Session.connection()
                    conn.execute(update)

                else:
                    insert = res_trans_table.insert()
                    insert = insert.values(lang_code = translation['lang_code'])
                    insert = insert.values(field = translation['field'])
                    insert = insert.values(field_translation = translation['field_translation'])
                    insert = insert.values(resource_id = translation['resource_id'])
                    insert = insert.values(resource_revision_id = translation['resource_revision_id'])

                    conn = model.Session.connection()
                    conn.execute(insert)

    model.Session.commit()

def get_langs_for_resource(context, resource_dict):
    if resource_dict:
        res_trans = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.lang_code)\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == resource_dict['id'])\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == resource_dict['revision_id'])\
            .distinct()

        result = res_trans.all()

        locales = config.get('ckan.locale_order', '')

        [x for (y,x) in sorted(zip(locales,result))]

        return result

def get_translated_field(context, dict):
    lang = dict['lang']
    resource_dict = dict['data_dict']
    field = dict['field']
    if 'remove_default' in dict:
        remove_default = True
    else:
        remove_default = False

    res_trans = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.field_translation)\
        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == resource_dict['id'])\
        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == resource_dict['revision_id'])\
        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.lang_code == lang)\
        .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.field == field)

    try:
        result = res_trans.distinct().one()
        return result
    except Exception:
        if not remove_default:
            return resource_dict['url']


def get_resources_with_translation(context, resource_list):
    if resource_list:
        for resource_dict in resource_list:
            res_trans = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table)\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == resource_dict['id'])\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == resource_dict['revision_id'])

            result = res_trans.all()

            for tuple in result:
                resource_dict[tuple[3]+'-'+tuple[5]] = tuple[4]

    return resource_list

def is_multi_languaged_resource(context, resource_dict):
    if resource_dict:
        result = model.Session.query(ckan_model.ecodp_resource_term_translation.resource_term_translation_table)\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_id == resource_dict['id'])\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.resource_revision_id == resource_dict['revision_id'])\
            .filter(ckan_model.ecodp_resource_term_translation.resource_term_translation_table.c.field == 'url')\
            .count()


        if result>0:
            return True

    return False

