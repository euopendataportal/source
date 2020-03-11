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

import ckan.model as model
import ckan.model.domain_object as domain_object
import ckan.model.types as _types
from sqlalchemy import Column, String, types
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Package_contact_info(Base,
                           domain_object.DomainObject):
    __tablename__ = 'package_contact_information'

    def __init__(self, user_id):
        self.user_id = user_id

    id = Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid)
    user_id = Column(String)
    contact_name = Column(String)
    contact_mailbox = Column(String)
    contact_phone_number = Column(String)
    contact_page = Column(String)
    contact_address = Column(String)

    def as_dict(self):
        return {'contact_name': self.contact_name or '',
                'contact_mailbox': self.contact_mailbox or '',
                'contact_phone_number': self.contact_phone_number or '',
                'contact_page': self.contact_page or '',
                'contact_address': self.contact_address or ''}

    def from_dict(self, reference_dict):
        self.contact_name = reference_dict.get('contact_name', '')
        self.contact_mailbox = reference_dict.get('contact_mailbox', '')
        self.contact_phone_number = reference_dict.get('contact_phone_number', '')
        self.contact_page = reference_dict.get('contact_page', '')
        self.contact_address = reference_dict.get('contact_address', '')

    @classmethod
    def get_by_user(cls, reference):
        '''Returns a package object referenced by its id or name.'''
        query = model.Session.query(cls).filter(cls.user_id == reference)
        obj = query.first()
        return obj
