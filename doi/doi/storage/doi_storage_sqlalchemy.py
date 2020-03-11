# -*- coding: utf-8 -*-
# Copyright (C) 2018  ARhS-CUBE

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

from doi_storage import DOIStorageInterface
import logging
import sqlalchemy
from doi.domain.doi_object import DOI
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String, Boolean, PrimaryKeyConstraint, UniqueConstraint, Index, desc, cast
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = None
session = None


class DOIStorageSQLAlchemy(DOIStorageInterface):

    def __init__(self, doi_db_connection_string):
        super(DOIStorageSQLAlchemy, self).__init__()
        self._doi_db_connection_string = doi_db_connection_string

    def _get_engine(self):
        global engine
        if not engine or engine is None:
            try:
                engine = sqlalchemy.create_engine(self._doi_db_connection_string)
                Base.metadata.create_all(engine)
                logging.info("Engine to postgresql is created")
            except Exception as e:
                logging.error("Database connection not found in config file; reason: {0}".format(e.message))
        return engine

    def _get_query_session(self):
        self._get_engine()
        assert engine is not None
        connection = engine.connect()
        assert connection is not None

        global session
        if session is None:
            session_factory = sessionmaker(bind=engine)
            session = session_factory()
            logging.info("Session for postgresql has been created")

        return session

    def save(self, doi):
        session = self._get_query_session()
        try:
            doi_entity = None
            if doi.get_uri() is not None:
                doi_entity = session.query(DOIEntity).filter_by(uri=doi.get_uri()).first()

            if doi_entity is None:
                doi_entity = DOIEntity(prefix=doi.get_prefix(), provider=doi.get_suffix_provider(), value=doi.get_suffix_element(), generated=True, uri=doi.get_uri())

            session.merge(doi_entity)
            session.commit()
        except Exception as e:
            logging.error('The system failed to save the DOI; reason: {0}'.format(e.message))
            session.rollback()
        finally:
            session.close()

    def find(self, **args):
        session = self._get_query_session()
        try:
            q = session.query(DOIEntity)
            if len(args) > 0:
                q = q.filter_by(**args)
            return [doi.to_doi_object() for doi in q.all()]
        except Exception as e:
            logging.error('The system failed to get DOIs; reason: {0}'.format(e.message))
        finally:
            session.close()

    def find_one(self, **args):
        session = self._get_query_session()
        try:
            doi = session.query(DOIEntity).filter_by(**args).first()
            if doi is None:
                return None
            return doi.to_doi_object()
        except Exception as e:
            logging.error('The system failed to get the DOI; reason: {0}'.format(e.message))
        finally:
            session.close()

    def next_doi(self, prefix, provider):
        session = self._get_query_session()
        try:
            doi = session.query(DOIEntity).filter_by(prefix=prefix, provider=provider, generated=True).order_by(desc(cast(DOIEntity.value, Integer))).first()
            if doi is None:
                doi = DOIEntity(prefix=prefix, provider=provider, value="1", generated=True, uri=None)
            else:
                doi = DOIEntity(prefix=prefix, provider=provider, value=str(int(doi.value)+1), generated=True, uri=None)

            if session.query(DOIEntity).filter_by(prefix=prefix, provider=provider, value=doi.value).first() is not None:
                raise Exception('The system provide an existing DOI')

            session.merge(doi)
            session.commit()
            return doi.to_doi_object()
        except Exception as e:
            logging.error('The system cannot provide a new DOI; reason: {0}'.format(e.message))
            session.rollback()
            raise
        finally:
            session.close()

    def delete(self, **args):
        session = self._get_query_session()
        try:
            entry = session.query(DOIEntity).filter_by(**args).first()
            if entry is not None:
                session.delete(entry)
            session.commit()
        except Exception as e:
            logging.error('The system failed to delete the DOI association; reason: {0}'.format(e.message))
            session.rollback()
            raise
        finally:
            session.close()

    def delete_all(self, **args):
        session = self._get_query_session()
        try:
            entries = session.query(DOIEntity).filter_by(**args).all()
            for entry in entries:
                session.delete(entry)
            session.commit()
        except Exception as e:
            logging.error('The system failed to delete DOI associations; reason: {0}'.format(e.message))
            session.rollback()
            raise
        finally:
            session.close()


class DOIEntity(Base):
    __tablename__ = u'doi'

    prefix = Column(String, nullable=False)
    provider = Column(String, nullable=False)
    value = Column(String, default="1")
    generated = Column(Boolean, default=False)
    uri = Column(String, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('prefix', 'provider', 'value'),
        UniqueConstraint('prefix', 'provider', 'value'),
        UniqueConstraint('uri'),
        Index('by_doi_index', 'prefix', 'provider', 'value'),
        Index('by_uri_index', 'uri'),
        Index('provider_index', 'prefix', 'provider'),
        {},
    )

    def to_doi_object(self):
        return DOI(self.prefix, self.provider, self.value, self.uri)
