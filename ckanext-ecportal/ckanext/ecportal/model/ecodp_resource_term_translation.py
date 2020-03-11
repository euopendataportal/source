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

import ckan.model.meta as meta
import ckan.model.types as _types
from sqlalchemy import types, Column, Table, ForeignKey

__all__ = ['resource_term_translation_table']

resource_term_translation_table = Table(
    'resource_term_translation', meta.metadata,
    Column('id', types.UnicodeText, primary_key=True, default=_types.make_uuid),
    Column('resource_id', types.UnicodeText, ForeignKey('resource.id')),
    Column('resource_revision_id', types.UnicodeText, ForeignKey('revision.id')),
    Column('field', types.UnicodeText),
    Column('field_translation', types.UnicodeText),
    Column('lang_code', types.UnicodeText),
)
