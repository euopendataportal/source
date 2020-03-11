# coding: utf-8
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

from sqlalchemy import BigInteger, Boolean, Column, Date, DateTime, Float, ForeignKey, Index, Integer, LargeBinary, SmallInteger, String, Table, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class Activity(Base):
    __tablename__ = u'activity'
    __table_args__ = (
        Index(u'idx_activity_object_id', u'timestamp', u'object_id'),
        Index(u'idx_activity_user_id', u'timestamp', u'user_id')
    )

    id = Column(Text, primary_key=True)
    timestamp = Column(DateTime)
    user_id = Column(Text)
    object_id = Column(Text)
    revision_id = Column(Text)
    activity_type = Column(Text)
    data = Column(Text)


class ActivityDetail(Base):
    __tablename__ = u'activity_detail'

    id = Column(Text, primary_key=True)
    activity_id = Column(ForeignKey(u'activity.id'), index=True)
    object_id = Column(Text)
    object_type = Column(Text)
    activity_type = Column(Text)
    data = Column(Text)

    activity = relationship(u'Activity')


class Archival(Base):
    __tablename__ = u'archival'

    id = Column(Text, primary_key=True)
    package_id = Column(Text, nullable=False, index=True)
    resource_id = Column(Text, nullable=False, index=True)
    resource_timestamp = Column(DateTime)
    status_id = Column(Integer)
    is_broken = Column(Boolean)
    reason = Column(Text)
    url_redirected_to = Column(Text)
    cache_filepath = Column(Text)
    cache_url = Column(Text)
    size = Column(BigInteger)
    mimetype = Column(Text)
    hash = Column(Text)
    etag = Column(Text)
    last_modified = Column(Text)
    first_failure = Column(DateTime)
    last_success = Column(DateTime)
    failure_count = Column(Integer)
    created = Column(DateTime)
    updated = Column(DateTime)


class AuthorizationGroup(Base):
    __tablename__ = u'authorization_group'

    id = Column(Text, primary_key=True)
    name = Column(Text)
    created = Column(DateTime)

    user_object_roles = relationship(u'UserObjectRole', secondary=u'authorization_group_role')


t_authorization_group_role = Table(
    u'authorization_group_role', metadata,
    Column(u'user_object_role_id', ForeignKey(u'user_object_role.id'), primary_key=True),
    Column(u'authorization_group_id', ForeignKey(u'authorization_group.id'))
)


class AuthorizationGroupUser(Base):
    __tablename__ = u'authorization_group_user'

    authorization_group_id = Column(ForeignKey(u'authorization_group.id'), nullable=False)
    user_id = Column(ForeignKey(u'user.id'), nullable=False)
    id = Column(Text, primary_key=True)

    authorization_group = relationship(u'AuthorizationGroup')
    user = relationship(u'User')


class CeleryTaskmeta(Base):
    __tablename__ = u'celery_taskmeta'

    id = Column(Integer, primary_key=True)
    task_id = Column(String(255), unique=True)
    status = Column(String(50))
    result = Column(LargeBinary)
    date_done = Column(DateTime)
    traceback = Column(Text)


class CeleryTasksetmeta(Base):
    __tablename__ = u'celery_tasksetmeta'

    id = Column(Integer, primary_key=True)
    taskset_id = Column(String(255), unique=True)
    result = Column(LargeBinary)
    date_done = Column(DateTime)


class Group(Base):
    __tablename__ = u'group'

    id = Column(Text, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)
    title = Column(Text)
    description = Column(Text)
    created = Column(DateTime)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))
    type = Column(Text, nullable=False, index=True)
    approval_status = Column(Text)
    image_url = Column(Text)
    is_organization = Column(Boolean, server_default=text("false"))

    revision = relationship(u'Revision')
    user_object_roles = relationship(u'UserObjectRole', secondary=u'group_role')


class GroupExtra(Base):
    __tablename__ = u'group_extra'

    id = Column(Text, primary_key=True)
    group_id = Column(ForeignKey(u'group.id'))
    key = Column(Text)
    value = Column(Text)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))

    group = relationship(u'Group')
    revision = relationship(u'Revision')


class GroupExtraRevision(Base):
    __tablename__ = u'group_extra_revision'
    __table_args__ = (
        Index(u'idx_group_extra_period', u'id', u'revision_timestamp', u'expired_timestamp'),
        Index(u'idx_group_extra_period_group', u'group_id', u'revision_timestamp', u'expired_timestamp')
    )

    id = Column(Text, primary_key=True, nullable=False)
    group_id = Column(ForeignKey(u'group.id'))
    key = Column(Text)
    value = Column(Text)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False)
    continuity_id = Column(ForeignKey(u'group_extra.id'))
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean, index=True)

    continuity = relationship(u'GroupExtra')
    group = relationship(u'Group')
    revision = relationship(u'Revision')


class GroupRevision(Base):
    __tablename__ = u'group_revision'
    __table_args__ = (
        Index(u'idx_group_period', u'id', u'revision_timestamp', u'expired_timestamp'),
    )

    id = Column(Text, primary_key=True, nullable=False)
    name = Column(Text, nullable=False)
    title = Column(Text)
    description = Column(Text)
    created = Column(DateTime)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False)
    continuity_id = Column(ForeignKey(u'group.id'))
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean, index=True)
    type = Column(Text, nullable=False)
    approval_status = Column(Text)
    image_url = Column(Text)
    is_organization = Column(Boolean, server_default=text("false"))

    continuity = relationship(u'Group')
    revision = relationship(u'Revision')


class GroupRole(Base):
    __tablename__ = u'group_role'
    user_object_role_id = Column(Text, ForeignKey(u'user_object_role.id'), primary_key=True)
    group_id = Column(Text, ForeignKey(u'group.id'), nullable=False)


class KombuMessage(Base):
    __tablename__ = u'kombu_message'

    id = Column(Integer, primary_key=True)
    visible = Column(Boolean, index=True)
    timestamp = Column(DateTime, index=True)
    payload = Column(Text, nullable=False)
    queue_id = Column(ForeignKey(u'kombu_queue.id'))
    version = Column(SmallInteger, nullable=False)

    queue = relationship(u'KombuQueue')


class KombuQueue(Base):
    __tablename__ = u'kombu_queue'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), unique=True)


class Member(Base):
    __tablename__ = u'member'
    __table_args__ = (
        Index(u'idx_package_group_pkg_id_group_id', u'table_id', u'group_id'),
        Index(u'idx_extra_grp_id_pkg_id', u'table_id', u'group_id')
    )

    id = Column(Text, primary_key=True, index=True)
    table_id = Column(Text, nullable=False, index=True)
    group_id = Column(ForeignKey(u'group.id'), index=True)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))
    table_name = Column(Text, nullable=False)
    capacity = Column(Text, nullable=False)

    group = relationship(u'Group')
    revision = relationship(u'Revision')


class MemberRevision(Base):
    __tablename__ = u'member_revision'

    id = Column(Text, primary_key=True, nullable=False, index=True)
    table_id = Column(Text, nullable=False)
    group_id = Column(ForeignKey(u'group.id'), index=True)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False)
    continuity_id = Column(ForeignKey(u'member.id'))
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean)
    table_name = Column(Text, nullable=False)
    capacity = Column(Text, nullable=False)

    continuity = relationship(u'Member')
    group = relationship(u'Group')
    revision = relationship(u'Revision')


class Package(Base):
    __tablename__ = u'package'

    id = Column(Text, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    title = Column(Text)
    version = Column(String(100))
    url = Column(Text, index=True)
    notes = Column(Text)
    license_id = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))
    author = Column(Text)
    author_email = Column(Text)
    maintainer = Column(Text)
    maintainer_email = Column(Text)
    state = Column(Text)
    type = Column(Text)
    owner_org = Column(Text)
    private = Column(Boolean, server_default=text("false"))
    metadata_modified = Column(DateTime)
    creator_user_id = Column(Text)
    revision = relationship(u'Revision')
    user_object_roles = relationship(u'UserObjectRole', secondary=u'package_role')


class PackageContactInformation(Base):
    __tablename__ = u'package_contact_information'

    id = Column(Text, primary_key=True)
    user_id = Column(ForeignKey(u'user.id'), nullable=False)
    contact_name = Column(Text)
    contact_mailbox = Column(Text)
    contact_phone_number = Column(Text)
    contact_page = Column(Text)
    contact_address = Column(Text)

    user = relationship(u'User')


class PackageExtra(Base):
    __tablename__ = u'package_extra'

    id = Column(Text, primary_key=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    key = Column(Text)
    value = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))
    state = Column(Text)

    package = relationship(u'Package')
    revision = relationship(u'Revision')

    def __getitem__(self):
        pass


class PackageExtraRevision(Base):
    __tablename__ = u'package_extra_revision'
    __table_args__ = (
        Index(u'idx_package_extra_package_id', u'package_id', u'current'),
    )

    id = Column(Text, primary_key=True, nullable=False, index=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    key = Column(Text)
    value = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False, index=True)
    continuity_id = Column(ForeignKey(u'package_extra.id'))
    state = Column(Text)
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean)

    continuity = relationship(u'PackageExtra')
    package = relationship(u'Package')
    revision = relationship(u'Revision')


class PackageRelationship(Base):
    __tablename__ = u'package_relationship'

    id = Column(Text, primary_key=True)
    subject_package_id = Column(ForeignKey(u'package.id'))
    object_package_id = Column(ForeignKey(u'package.id'))
    type = Column(Text)
    comment = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))
    state = Column(Text)

    object_package = relationship(u'Package', primaryjoin='PackageRelationship.object_package_id == Package.id')
    revision = relationship(u'Revision')
    subject_package = relationship(u'Package', primaryjoin='PackageRelationship.subject_package_id == Package.id')


class PackageRelationshipRevision(Base):
    __tablename__ = u'package_relationship_revision'
    __table_args__ = (
        Index(u'idx_period_package_relationship', u'subject_package_id', u'object_package_id', u'revision_timestamp', u'expired_timestamp'),
    )

    id = Column(Text, primary_key=True, nullable=False)
    subject_package_id = Column(ForeignKey(u'package.id'))
    object_package_id = Column(ForeignKey(u'package.id'))
    type = Column(Text)
    comment = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False)
    continuity_id = Column(ForeignKey(u'package_relationship.id'))
    state = Column(Text)
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean, index=True)

    continuity = relationship(u'PackageRelationship')
    object_package = relationship(u'Package', primaryjoin='PackageRelationshipRevision.object_package_id == Package.id')
    revision = relationship(u'Revision')
    subject_package = relationship(u'Package', primaryjoin='PackageRelationshipRevision.subject_package_id == Package.id')


class PackageRevision(Base):
    __tablename__ = u'package_revision'
    __table_args__ = (
        Index(u'idx_package_period', u'id', u'revision_timestamp', u'expired_timestamp'),
    )

    id = Column(Text, primary_key=True, nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    title = Column(Text)
    version = Column(String(100))
    url = Column(Text)
    notes = Column(Text)
    license_id = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False, index=True)
    continuity_id = Column(ForeignKey(u'package.id'))
    author = Column(Text)
    author_email = Column(Text)
    maintainer = Column(Text)
    maintainer_email = Column(Text)
    state = Column(Text)
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean, index=True)
    type = Column(Text)
    owner_org = Column(Text)
    private = Column(Boolean, server_default=text("false"))
    metadata_modified = Column(DateTime)
    creator_user_id = Column(Text)

    continuity = relationship(u'Package')
    revision = relationship(u'Revision')


class PackageRole(Base):
    __tablename__ = u'package_role'
    user_object_role_id = Column(Text, ForeignKey(u'user_object_role.id'), primary_key=True)
    package_id = Column(Text, ForeignKey(u'package.id'), nullable=False)


class PackageTag(Base):
    __tablename__ = u'package_tag'
    __table_args__ = (
        Index(u'idx_package_tag_pkg_id_tag_id', u'package_id', u'tag_id'),
    )

    id = Column(Text, primary_key=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    tag_id = Column(ForeignKey(u'tag.id'), index=True)
    revision_id = Column(ForeignKey(u'revision.id'))
    state = Column(Text)

    package = relationship(u'Package')
    revision = relationship(u'Revision')
    tag = relationship(u'Tag')


class PackageTagRevision(Base):
    __tablename__ = u'package_tag_revision'

    id = Column(Text, primary_key=True, nullable=False, index=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    tag_id = Column(ForeignKey(u'tag.id'), index=True)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False, index=True)
    continuity_id = Column(ForeignKey(u'package_tag.id'))
    state = Column(Text)
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean)

    continuity = relationship(u'PackageTag')
    package = relationship(u'Package')
    revision = relationship(u'Revision')
    tag = relationship(u'Tag')


class Permalink(Base):
    __tablename__ = u'permalinks'

    link_hash = Column(Text, primary_key=True)
    ip = Column(Text, nullable=False)
    state = Column(Text, nullable=False)
    time = Column(DateTime, server_default=text("now()"))


class QueryCache(Base):
    __tablename__ = u'query_cache'

    query_hash = Column(LargeBinary, primary_key=True)
    query_string = Column(String(16383))
    data = Column(LargeBinary)
    time = Column(DateTime)


class Rating(Base):
    __tablename__ = u'rating'

    id = Column(Text, primary_key=True, index=True)
    user_id = Column(ForeignKey(u'user.id'), index=True)
    user_ip_address = Column(Text)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    rating = Column(Float(53))
    created = Column(DateTime)

    package = relationship(u'Package')
    user = relationship(u'User')


class Related(Base):
    __tablename__ = u'related'

    id = Column(Text, primary_key=True)
    type = Column(Text, nullable=False)
    title = Column(Text)
    description = Column(Text)
    image_url = Column(Text)
    url = Column(Text)
    created = Column(DateTime)
    owner_id = Column(Text)
    view_count = Column(Integer, nullable=False, server_default=text("0"))
    featured = Column(Integer, nullable=False, server_default=text("0"))


class RelatedDataset(Base):
    __tablename__ = u'related_dataset'

    id = Column(Text, primary_key=True)
    dataset_id = Column(ForeignKey(u'package.id'), nullable=False)
    related_id = Column(ForeignKey(u'related.id'), nullable=False)
    status = Column(Text)

    dataset = relationship(u'Package')
    related = relationship(u'Related')


class Resource(Base):
    __tablename__ = u'resource'

    id = Column(Text, primary_key=True, index=True)
    resource_group_id = Column(ForeignKey(u'resource_group.id'), index=True)
    url = Column(Text, nullable=False, index=True)
    format = Column(Text)
    description = Column(Text)
    position = Column(Integer)
    revision_id = Column(ForeignKey(u'revision.id'))
    hash = Column(Text)
    state = Column(Text)
    extras = Column(Text)
    name = Column(Text, index=True)
    resource_type = Column(Text)
    mimetype = Column(Text)
    mimetype_inner = Column(Text)
    size = Column(BigInteger)
    last_modified = Column(DateTime)
    cache_url = Column(Text)
    cache_last_updated = Column(DateTime)
    webstore_url = Column(Text)
    webstore_last_updated = Column(DateTime)
    created = Column(DateTime)
    url_type = Column(Text)
    resource_count = Column(BigInteger, server_default=text("0"))

    resource_group = relationship(u'ResourceGroup')
    revision = relationship(u'Revision')


class ResourceGroup(Base):
    __tablename__ = u'resource_group'

    id = Column(Text, primary_key=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    label = Column(Text)
    sort_order = Column(Text)
    extras = Column(Text)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))

    package = relationship(u'Package')
    revision = relationship(u'Revision')


class ResourceGroupRevision(Base):
    __tablename__ = u'resource_group_revision'

    id = Column(Text, primary_key=True, nullable=False, index=True)
    package_id = Column(ForeignKey(u'package.id'), index=True)
    label = Column(Text)
    sort_order = Column(Text)
    extras = Column(Text)
    state = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False, index=True)
    continuity_id = Column(ForeignKey(u'resource_group.id'))
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean)

    continuity = relationship(u'ResourceGroup')
    package = relationship(u'Package')
    revision = relationship(u'Revision')


class ResourceRevision(Base):
    __tablename__ = u'resource_revision'
    __table_args__ = (
        Index(u'idx_resource_resource_group_id', u'resource_group_id', u'current'),
    )

    id = Column(Text, primary_key=True, nullable=False, index=True)
    resource_group_id = Column(ForeignKey(u'resource_group.id'), index=True)
    url = Column(Text, nullable=False)
    format = Column(Text)
    description = Column(Text)
    position = Column(Integer)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False, index=True)
    continuity_id = Column(ForeignKey(u'resource.id'))
    hash = Column(Text)
    state = Column(Text)
    extras = Column(Text)
    expired_id = Column(Text)
    revision_timestamp = Column(DateTime)
    expired_timestamp = Column(DateTime)
    current = Column(Boolean)
    name = Column(Text)
    resource_type = Column(Text)
    mimetype = Column(Text)
    mimetype_inner = Column(Text)
    size = Column(BigInteger)
    last_modified = Column(DateTime)
    cache_url = Column(Text)
    cache_last_updated = Column(DateTime)
    webstore_url = Column(Text)
    webstore_last_updated = Column(DateTime)
    created = Column(DateTime)
    url_type = Column(Text)

    continuity = relationship(u'Resource')
    resource_group = relationship(u'ResourceGroup')
    revision = relationship(u'Revision')


class ResourceTermTranslation(Base):
    __tablename__ = u'resource_term_translation'
    __table_args__ = (
        Index(u'UNIQUE_KEY', u'resource_id', u'resource_revision_id', u'field', u'lang_code', unique=True),
    )

    id = Column(Text, primary_key=True)
    resource_id = Column(ForeignKey(u'resource.id'), nullable=False)
    resource_revision_id = Column(ForeignKey(u'revision.id'), nullable=False)
    field = Column(Text, nullable=False)
    field_translation = Column(Text, nullable=False)
    lang_code = Column(Text, nullable=False)

    resource = relationship(u'Resource')
    resource_revision = relationship(u'Revision')


class Revision(Base):
    __tablename__ = u'revision'

    id = Column(Text, primary_key=True, index=True)
    timestamp = Column(DateTime)
    author = Column(String(200), index=True)
    message = Column(Text)
    state = Column(Text, index=True)
    approved_timestamp = Column(DateTime)


class RoleAction(Base):
    __tablename__ = u'role_action'
    __table_args__ = (
        Index(u'idx_ra_role_action', u'role', u'action'),
    )

    id = Column(Text, primary_key=True)
    role = Column(Text, index=True)
    context = Column(Text, nullable=False)
    action = Column(Text, index=True)


t_search_popular_approved = Table(
    u'search_popular_approved', metadata,
    Column(u'lang', String(10)),
    Column(u'search_string', String, nullable=False),
    Column(u'count', BigInteger, nullable=False)
)


t_search_popular_latest = Table(
    u'search_popular_latest', metadata,
    Column(u'lang', String(10)),
    Column(u'search_string', String, nullable=False),
    Column(u'count', BigInteger)
)


t_search_query = Table(
    u'search_query', metadata,
    Column(u'lang', String(10), nullable=False),
    Column(u'search_string', String, nullable=False),
    Column(u'searched_at', DateTime, index=True, server_default=text("now()"))
)


class SystemInfo(Base):
    __tablename__ = u'system_info'

    id = Column(Integer, primary_key=True, server_default=text("nextval('system_info_id_seq'::regclass)"))
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'))

    revision = relationship(u'Revision')


class SystemInfoRevision(Base):
    __tablename__ = u'system_info_revision'

    id = Column(Integer, primary_key=True, nullable=False, server_default=text("nextval('system_info_revision_id_seq'::regclass)"))
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text)
    revision_id = Column(ForeignKey(u'revision.id'), primary_key=True, nullable=False)
    continuity_id = Column(ForeignKey(u'system_info.id'))

    continuity = relationship(u'SystemInfo')
    revision = relationship(u'Revision')


class Tag(Base):
    __tablename__ = u'tag'
    __table_args__ = (
        Index(u'tag_name_vocabulary_id_key', u'name', u'vocabulary_id', unique=True),
    )

    id = Column(Text, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    vocabulary_id = Column(ForeignKey(u'vocabulary.id'))

    vocabulary = relationship(u'Vocabulary')


class TaskStatus(Base):
    __tablename__ = u'task_status'
    __table_args__ = (
        Index(u'task_status_entity_id_task_type_key_key', u'entity_id', u'task_type', u'key', unique=True),
    )

    id = Column(Text, primary_key=True)
    entity_id = Column(Text, nullable=False)
    entity_type = Column(Text, nullable=False)
    task_type = Column(Text, nullable=False)
    key = Column(Text, nullable=False)
    value = Column(Text, nullable=False)
    state = Column(Text)
    error = Column(Text)
    last_updated = Column(DateTime)


class TermTranslation(Base):
    __tablename__ = u'term_translation'
    __table_args__ = (
        Index(u'term_lang', u'term', u'lang_code'),
    )

    term = Column(Text, nullable=False)
    term_translation = Column(Text, nullable=False)
    lang_code = Column(Text, nullable=False, primary_key=True)

t_tracking_raw = Table(
    u'tracking_raw', metadata,
    Column(u'user_key', String(100), nullable=False, index=True),
    Column(u'url', Text, nullable=False, index=True),
    Column(u'tracking_type', String(10), nullable=False),
    Column(u'access_timestamp', DateTime, index=True, server_default=text("now()"))
)


t_tracking_summary = Table(
    u'tracking_summary', metadata,
    Column(u'url', Text, nullable=False, index=True),
    Column(u'package_id', Text, index=True),
    Column(u'tracking_type', String(10), nullable=False),
    Column(u'count', Integer, nullable=False),
    Column(u'running_total', Integer, nullable=False, server_default=text("0")),
    Column(u'recent_views', Integer, nullable=False, server_default=text("0")),
    Column(u'tracking_date', Date, index=True)
)


class User(Base):
    __tablename__ = u'user'

    id = Column(Text, primary_key=True, index=True)
    name = Column(Text, nullable=False, unique=True)
    apikey = Column(Text)
    created = Column(DateTime)
    about = Column(Text)
    openid = Column(Text, index=True)
    password = Column(Text)
    fullname = Column(Text)
    email = Column(Text)
    reset_key = Column(Text)
    sysadmin = Column(Boolean, server_default=text("false"))
    activity_streams_email_notifications = Column(Boolean, server_default=text("false"))
    state = Column(Text, nullable=False, server_default=text("'active'::text"))


class Dashboard(User):
    __tablename__ = u'dashboard'

    user_id = Column(ForeignKey(u'user.id'), primary_key=True)
    activity_stream_last_viewed = Column(DateTime, nullable=False)
    email_last_sent = Column(DateTime, nullable=False, server_default=text("('now'::text)::timestamp without time zone"))


class UserFollowingDataset(Base):
    __tablename__ = u'user_following_dataset'

    follower_id = Column(ForeignKey(u'user.id'), primary_key=True, nullable=False)
    object_id = Column(ForeignKey(u'package.id'), primary_key=True, nullable=False)
    datetime = Column(DateTime, nullable=False)

    follower = relationship(u'User')
    object = relationship(u'Package')


class UserFollowingGroup(Base):
    __tablename__ = u'user_following_group'

    follower_id = Column(ForeignKey(u'user.id'), primary_key=True, nullable=False)
    object_id = Column(ForeignKey(u'group.id'), primary_key=True, nullable=False)
    datetime = Column(DateTime, nullable=False)

    follower = relationship(u'User')
    object = relationship(u'Group')


class UserFollowingUser(Base):
    __tablename__ = u'user_following_user'

    follower_id = Column(ForeignKey(u'user.id'), primary_key=True, nullable=False)
    object_id = Column(ForeignKey(u'user.id'), primary_key=True, nullable=False)
    datetime = Column(DateTime, nullable=False)

    follower = relationship(u'User', primaryjoin='UserFollowingUser.follower_id == User.id')
    object = relationship(u'User', primaryjoin='UserFollowingUser.object_id == User.id')


class UserObjectRole(Base):
    __tablename__ = u'user_object_role'
    __table_args__ = (
        Index(u'idx_uor_user_id_role', u'user_id', u'role'),
    )

    id = Column(Text, primary_key=True, index=True)
    user_id = Column(ForeignKey(u'user.id'), index=True)
    context = Column(Text, nullable=False, index=True)
    role = Column(Text, index=True)
    authorized_group_id = Column(ForeignKey(u'authorization_group.id'))

    authorized_group = relationship(u'AuthorizationGroup')
    user = relationship(u'User')


class SystemRole(UserObjectRole):
    __tablename__ = u'system_role'

    user_object_role_id = Column(ForeignKey(u'user_object_role.id'), primary_key=True)


class Vocabulary(Base):
    __tablename__ = u'vocabulary'

    id = Column(Text, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
