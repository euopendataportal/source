# -*- coding: utf-8 -*-
# Copyright (C) 2019  Publications Office of the European Union

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>
from sqlalchemy import Column, Table, String, MetaData
from sqlalchemy.types import UnicodeText
import ckan.model as model
from sqlalchemy.orm import mapper
from sqlalchemy.orm import mapper
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class DatasetIdMapping(object):


    def __init__(self, external_id, internal_id, publisher):
        self.external_id = external_id
        self.internal_id = internal_id
        self.publisher = publisher

    def __repr__(self):
        return '<DatasetIdMapping(external_id = {0}, internal_id= {1})>'.format(self.external_id, self.internal_id)

    @classmethod
    def by_external_id(cls, external_id, autoflush=True):
        """"""
        str_query = 'select external_id, internal_id, publisher from dataset_id_mapping where external_id = :external_id'
        result = model.Session.execute(str_query, {'external_id': external_id})
        mapping = None
        for row in result:
            mapping = DatasetIdMapping(row[0], row[1], row[2])
        return mapping

    @classmethod
    def by_internal_id(cls, internal_id, autoflush=True):
        """"""
        str_query = 'select external_id, internal_id, publisher from dataset_id_mapping where internal_id = :internal_id'
        result = model.Session.execute(str_query, {'internal_id': internal_id})
        mapping = None
        for row in result:
            mapping = DatasetIdMapping(row[0], row[1], row[2])
        return mapping

    @classmethod
    def get_dict_of_mappings_by_publisher(self, publisher):
        str_query = 'select external_id, internal_id , publisher from dataset_id_mapping where publisher = :publisher'
        result = model.Session.execute(str_query, {'publisher': publisher})
        mapping = {}
        for row in result:
            mapping[row[1]] = {'external_id': row[0],
                               'publisher': row[2]}
        return mapping


    def save_to_db(self):

        str_query = 'insert into dataset_id_mapping (external_id, internal_id, publisher) values (:external_id, :internal_id, :publisher) '
        session = model.Session
        result = session.execute(str_query, {'external_id': self.external_id, 'internal_id': self.internal_id, 'publisher': self.publisher})
        session.commit()
        return result


    def update_db(self):
        str_query = 'update dataset_id_mapping set external_id = :external_id, publisher = :publisher  where internal_id = :internal_id '
        session = model.Session
        result = session.execute(str_query, {'external_id': self.external_id, 'internal_id': self.internal_id, 'publisher':self.publisher})
        session.commit()
        return result

    def delete_from_db(self):
        str_query = 'delete from dataset_id_mapping  where external_id = :external_id '
        session = model.Session
        result = session.execute(str_query, {'external_id': self.external_id})
        session.commit()
        return result

    def is_mapping_exists(self):
        str_query = 'select external_id, internal_id, publisher from dataset_id_mapping where publisher = :publisher and (internal_id = :internal_id or external_id = :external_id) limit 1'
        result = model.Session.execute(str_query, {'external_id': self.external_id, 'internal_id': self.internal_id, 'publisher': self.publisher})
        return result.rowcount > 0
