
-- Drop table

-- DROP TABLE public.activity;

CREATE TABLE public.activity (
	id text NOT NULL,
	"timestamp" timestamp NULL,
	user_id text NULL,
	object_id text NULL,
	revision_id text NULL,
	activity_type text NULL,
	"data" text NULL,
	CONSTRAINT activity_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_activity_object_id ON activity USING btree (object_id, "timestamp");
CREATE INDEX idx_activity_user_id ON activity USING btree (user_id, "timestamp");

-- Drop table

-- DROP TABLE public.archival;

CREATE TABLE public.archival (
	id text NOT NULL,
	package_id text NOT NULL,
	resource_id text NOT NULL,
	resource_timestamp timestamp NULL,
	status_id int4 NULL,
	is_broken bool NULL,
	reason text NULL,
	url_redirected_to text NULL,
	cache_filepath text NULL,
	cache_url text NULL,
	"size" int8 NULL,
	mimetype text NULL,
	hash text NULL,
	etag text NULL,
	last_modified text NULL,
	first_failure timestamp NULL,
	last_success timestamp NULL,
	failure_count int4 NULL,
	created timestamp NULL,
	updated timestamp NULL,
	CONSTRAINT archival_pkey PRIMARY KEY (id)
);
CREATE INDEX ix_archival_package_id ON archival USING btree (package_id);
CREATE INDEX ix_archival_resource_id ON archival USING btree (resource_id);

-- Drop table

-- DROP TABLE public.authorization_group;

CREATE TABLE public.authorization_group (
	id text NOT NULL,
	name text NULL,
	created timestamp NULL,
	CONSTRAINT authorization_group_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.celery_taskmeta;

CREATE TABLE public.celery_taskmeta (
	id int4 NOT NULL,
	task_id varchar(255) NULL,
	status varchar(50) NULL,
	"result" bytea NULL,
	date_done timestamp NULL,
	traceback text NULL,
	CONSTRAINT celery_taskmeta_pkey PRIMARY KEY (id),
	CONSTRAINT celery_taskmeta_task_id_key UNIQUE (task_id)
);

-- Drop table

-- DROP TABLE public.celery_tasksetmeta;

CREATE TABLE public.celery_tasksetmeta (
	id int4 NOT NULL,
	taskset_id varchar(255) NULL,
	"result" bytea NULL,
	date_done timestamp NULL,
	CONSTRAINT celery_tasksetmeta_pkey PRIMARY KEY (id),
	CONSTRAINT celery_tasksetmeta_taskset_id_key UNIQUE (taskset_id)
);

-- Drop table

-- DROP TABLE public.checker_link_metadata;

CREATE TABLE public.checker_link_metadata (
	url text NOT NULL,
	"comment" text NULL,
	failed_attempts int4 NOT NULL,
	last_verification_time timestamp NULL,
	resource_title text NULL,
	status varchar(255) NULL,
	CONSTRAINT checker_link_metadata_pkey PRIMARY KEY (url)
);
CREATE INDEX link_url_index ON checker_link_metadata USING btree (url);

-- Drop table

-- DROP TABLE public.checker_organisation;

CREATE TABLE public.checker_organisation (
	uri text NOT NULL,
	name text NULL,
	CONSTRAINT checker_organisation_pkey PRIMARY KEY (uri)
);

-- Drop table

-- DROP TABLE public.dataset_id_mapping;

CREATE TABLE public.dataset_id_mapping (
	external_id text NOT NULL,
	internal_id text NOT NULL,
	publisher text NOT NULL,
	CONSTRAINT external_id_pkey PRIMARY KEY (external_id)
);
CREATE UNIQUE INDEX dataset_id_mapping_internal_id_uindex ON dataset_id_mapping USING btree (internal_id);
CREATE INDEX dataset_id_mapping_publisher_index ON dataset_id_mapping USING btree (publisher);

-- Drop table

-- DROP TABLE public.doi;

CREATE TABLE public.doi (
	prefix varchar NOT NULL,
	provider varchar NOT NULL,
	value varchar NOT NULL,
	"generated" bool NULL,
	uri varchar NULL,
	CONSTRAINT doi_pkey PRIMARY KEY (prefix, provider, value),
	CONSTRAINT doi_uri_key UNIQUE (uri)
);
CREATE INDEX by_doi_index ON doi USING btree (prefix, provider, value);
CREATE INDEX by_uri_index ON doi USING btree (uri);
CREATE INDEX provider_index ON doi USING btree (prefix, provider);

-- Drop table

-- DROP TABLE public.kombu_queue;

CREATE TABLE public.kombu_queue (
	id int4 NOT NULL,
	name varchar(200) NULL,
	CONSTRAINT kombu_queue_name_key UNIQUE (name),
	CONSTRAINT kombu_queue_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.migrate_version;

CREATE TABLE public.migrate_version (
	repository_id varchar(250) NOT NULL,
	repository_path text NULL,
	"version" int4 NULL,
	CONSTRAINT migrate_version_pkey PRIMARY KEY (repository_id)
);

-- Drop table

-- DROP TABLE public.permalinks;

CREATE TABLE public.permalinks (
	link_hash text NOT NULL,
	ip text NOT NULL,
	state text NOT NULL,
	"time" timestamp NULL DEFAULT now(),
	CONSTRAINT permalinks_pkey PRIMARY KEY (link_hash)
);

-- Drop table

-- DROP TABLE public.query_cache;

CREATE TABLE public.query_cache (
	query_hash bytea NOT NULL,
	query_string varchar(16383) NULL,
	"data" bytea NULL,
	"time" timestamp NULL,
	CONSTRAINT query_cache_pkey PRIMARY KEY (query_hash)
);

-- Drop table

-- DROP TABLE public.related;

CREATE TABLE public.related (
	id text NOT NULL,
	"type" text NOT NULL,
	title text NULL,
	description text NULL,
	image_url text NULL,
	url text NULL,
	created timestamp NULL,
	owner_id text NULL,
	view_count int4 NOT NULL DEFAULT 0,
	featured int4 NOT NULL DEFAULT 0,
	CONSTRAINT related_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.resource_download_count;

CREATE TABLE public.resource_download_count (
	resource_id text NOT NULL,
	resource_count int4 NOT NULL DEFAULT 0,
	dataset_id text NOT NULL DEFAULT ''::text,
	CONSTRAINT resource_download_count_pkey PRIMARY KEY (resource_id)
);
CREATE UNIQUE INDEX resource_download_count_resource_id_uindex ON resource_download_count USING btree (resource_id);

-- Drop table

-- DROP TABLE public.revision;

CREATE TABLE public.revision (
	id text NOT NULL,
	"timestamp" timestamp NULL,
	author varchar(200) NULL,
	message text NULL,
	state text NULL,
	approved_timestamp timestamp NULL,
	CONSTRAINT revision_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.role_action;

CREATE TABLE public.role_action (
	id text NOT NULL,
	"role" text NULL,
	context text NOT NULL,
	"action" text NULL,
	CONSTRAINT role_action_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_ra_action ON role_action USING btree (action);
CREATE INDEX idx_ra_role ON role_action USING btree (role);
CREATE INDEX idx_ra_role_action ON role_action USING btree (action, role);

-- Drop table

-- DROP TABLE public.search_popular_approved;

CREATE TABLE public.search_popular_approved (
	lang varchar(10) NULL,
	search_string varchar NOT NULL,
	count int8 NOT NULL
);

-- Drop table

-- DROP TABLE public.search_popular_latest;

CREATE TABLE public.search_popular_latest (
	lang varchar(10) NULL,
	search_string varchar NOT NULL,
	count int8 NULL
);

-- Drop table

-- DROP TABLE public.search_query;

CREATE TABLE public.search_query (
	lang varchar(10) NOT NULL,
	search_string varchar NOT NULL,
	searched_at timestamp NULL DEFAULT now()
);

-- Drop table

-- DROP TABLE public.task_status;

CREATE TABLE public.task_status (
	id text NOT NULL,
	entity_id text NOT NULL,
	entity_type text NOT NULL,
	task_type text NOT NULL,
	"key" text NOT NULL,
	value text NOT NULL,
	state text NULL,
	error text NULL,
	last_updated timestamp NULL,
	CONSTRAINT task_status_entity_id_task_type_key_key UNIQUE (entity_id, task_type, key),
	CONSTRAINT task_status_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.term_translation;

CREATE TABLE public.term_translation (
	term text NOT NULL,
	term_translation text NOT NULL,
	lang_code text NOT NULL
);

-- Drop table

-- DROP TABLE public.tracking_raw;

CREATE TABLE public.tracking_raw (
	user_key varchar(100) NOT NULL,
	url text NOT NULL,
	tracking_type varchar(10) NOT NULL,
	access_timestamp timestamp NULL DEFAULT now()
);

-- Drop table

-- DROP TABLE public.tracking_summary;

CREATE TABLE public.tracking_summary (
	url text NOT NULL,
	package_id text NULL,
	tracking_type varchar(10) NOT NULL,
	count int4 NOT NULL,
	running_total int4 NOT NULL DEFAULT 0,
	recent_views int4 NOT NULL DEFAULT 0,
	tracking_date date NULL
);

-- Drop table

-- DROP TABLE public."user";

CREATE TABLE public."user" (
	id text NOT NULL,
	name text NOT NULL,
	apikey text NULL,
	created timestamp NULL,
	about text NULL,
	openid text NULL,
	"password" text NULL,
	fullname text NULL,
	email text NULL,
	reset_key text NULL,
	sysadmin bool NULL DEFAULT false,
	activity_streams_email_notifications bool NULL DEFAULT false,
	state text NOT NULL DEFAULT 'active'::text,
	CONSTRAINT user_name_key UNIQUE (name),
	CONSTRAINT user_pkey PRIMARY KEY (id)
);
CREATE INDEX idx_openid ON "user" USING btree (openid);
CREATE INDEX idx_user_id ON "user" USING btree (id);
CREATE INDEX idx_user_name ON "user" USING btree (name);
CREATE INDEX idx_user_name_index ON "user" USING btree ((
CASE
    WHEN ((fullname IS NULL) OR (fullname = ''::text)) THEN name
    ELSE fullname
END));

-- Drop table

-- DROP TABLE public.vocabulary;

CREATE TABLE public.vocabulary (
	id text NOT NULL,
	name varchar(100) NOT NULL,
	CONSTRAINT vocabulary_name_key UNIQUE (name),
	CONSTRAINT vocabulary_pkey PRIMARY KEY (id)
);

-- Drop table

-- DROP TABLE public.activity_detail;

CREATE TABLE public.activity_detail (
	id text NOT NULL,
	activity_id text NULL,
	object_id text NULL,
	object_type text NULL,
	activity_type text NULL,
	"data" text NULL,
	CONSTRAINT activity_detail_pkey PRIMARY KEY (id),
	CONSTRAINT activity_detail_activity_id_fkey FOREIGN KEY (activity_id) REFERENCES activity(id)
);
CREATE INDEX idx_activity_detail_activity_id ON activity_detail USING btree (activity_id);

-- Drop table

-- DROP TABLE public.authorization_group_user;

CREATE TABLE public.authorization_group_user (
	authorization_group_id text NOT NULL,
	user_id text NOT NULL,
	id text NOT NULL,
	CONSTRAINT authorization_group_user_pkey PRIMARY KEY (id),
	CONSTRAINT authorization_group_user_authorization_group_id_fkey FOREIGN KEY (authorization_group_id) REFERENCES authorization_group(id),
	CONSTRAINT authorization_group_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id)
);

-- Drop table

-- DROP TABLE public.checker_dataset;

CREATE TABLE public.checker_dataset (
	uri text NOT NULL,
	name text NULL,
	organisation_id text NULL,
	CONSTRAINT checker_dataset_pkey PRIMARY KEY (uri),
	CONSTRAINT fktq8dhqd809tw00se3q3vstloi FOREIGN KEY (organisation_id) REFERENCES checker_organisation(uri)
);
CREATE INDEX dataset_organisation_id_index ON checker_dataset USING btree (organisation_id);
CREATE INDEX dataset_uri_index ON checker_dataset USING btree (uri);

-- Drop table

-- DROP TABLE public.checker_dataset_link;

CREATE TABLE public.checker_dataset_link (
	link_url text NOT NULL,
	dataset_uri text NOT NULL,
	CONSTRAINT fkem2dqaglaccvjwrjbfp7rpey6 FOREIGN KEY (link_url) REFERENCES checker_link_metadata(url),
	CONSTRAINT fkp9glesvy3dtqpu4ld9wldrl84 FOREIGN KEY (dataset_uri) REFERENCES checker_dataset(uri)
);

-- Drop table

-- DROP TABLE public.dashboard;

CREATE TABLE public.dashboard (
	user_id text NOT NULL,
	activity_stream_last_viewed timestamp NOT NULL,
	email_last_sent timestamp NOT NULL DEFAULT 'now'::text::timestamp without time zone,
	CONSTRAINT dashboard_pkey PRIMARY KEY (user_id),
	CONSTRAINT dashboard_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public."group";

CREATE TABLE public."group" (
	id text NOT NULL,
	name text NOT NULL,
	title text NULL,
	description text NULL,
	created timestamp NULL,
	state text NULL,
	revision_id text NULL,
	"type" text NOT NULL,
	approval_status text NULL,
	image_url text NULL,
	is_organization bool NULL DEFAULT false,
	CONSTRAINT group_name_key UNIQUE (name),
	CONSTRAINT group_pkey PRIMARY KEY (id),
	CONSTRAINT group_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_group_id ON "group" USING btree (id);
CREATE INDEX idx_group_name ON "group" USING btree (name);
CREATE INDEX ix_group_type ON "group" USING btree (type);

-- Drop table

-- DROP TABLE public.group_extra;

CREATE TABLE public.group_extra (
	id text NOT NULL,
	group_id text NULL,
	"key" text NULL,
	value text NULL,
	state text NULL,
	revision_id text NULL,
	CONSTRAINT group_extra_pkey PRIMARY KEY (id),
	CONSTRAINT group_extra_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id),
	CONSTRAINT group_extra_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);

-- Drop table

-- DROP TABLE public.group_extra_revision;

CREATE TABLE public.group_extra_revision (
	id text NOT NULL,
	group_id text NULL,
	"key" text NULL,
	value text NULL,
	state text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	CONSTRAINT group_extra_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT group_extra_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES group_extra(id),
	CONSTRAINT group_extra_revision_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id),
	CONSTRAINT group_extra_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_group_extra_current ON group_extra_revision USING btree (current);
CREATE INDEX idx_group_extra_period ON group_extra_revision USING btree (revision_timestamp, expired_timestamp, id);
CREATE INDEX idx_group_extra_period_group ON group_extra_revision USING btree (revision_timestamp, expired_timestamp, group_id);

-- Drop table

-- DROP TABLE public.group_revision;

CREATE TABLE public.group_revision (
	id text NOT NULL,
	name text NOT NULL,
	title text NULL,
	description text NULL,
	created timestamp NULL,
	state text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	"type" text NOT NULL,
	approval_status text NULL,
	image_url text NULL,
	is_organization bool NULL DEFAULT false,
	CONSTRAINT group_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT group_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES "group"(id),
	CONSTRAINT group_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_group_current ON group_revision USING btree (current);
CREATE INDEX idx_group_period ON group_revision USING btree (revision_timestamp, expired_timestamp, id);

-- Drop table

-- DROP TABLE public.kombu_message;

CREATE TABLE public.kombu_message (
	id int4 NOT NULL,
	visible bool NULL,
	"timestamp" timestamp NULL,
	payload text NOT NULL,
	queue_id int4 NULL,
	"version" int2 NOT NULL,
	CONSTRAINT kombu_message_pkey PRIMARY KEY (id),
	CONSTRAINT "FK_kombu_message_queue" FOREIGN KEY (queue_id) REFERENCES kombu_queue(id)
);

-- Drop table

-- DROP TABLE public."member";

CREATE TABLE public."member" (
	id text NOT NULL,
	table_id text NOT NULL,
	group_id text NULL,
	state text NULL,
	revision_id text NULL,
	table_name text NOT NULL,
	capacity text NOT NULL,
	CONSTRAINT member_pkey PRIMARY KEY (id),
	CONSTRAINT member_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id),
	CONSTRAINT member_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_extra_grp_id_pkg_id ON member USING btree (group_id, table_id);
CREATE INDEX idx_group_pkg_id ON member USING btree (table_id);
CREATE INDEX idx_package_group_group_id ON member USING btree (group_id);
CREATE INDEX idx_package_group_id ON member USING btree (id);
CREATE INDEX idx_package_group_pkg_id ON member USING btree (table_id);
CREATE INDEX idx_package_group_pkg_id_group_id ON member USING btree (group_id, table_id);

-- Drop table

-- DROP TABLE public.member_revision;

CREATE TABLE public.member_revision (
	id text NOT NULL,
	table_id text NOT NULL,
	group_id text NULL,
	state text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	table_name text NOT NULL,
	capacity text NOT NULL,
	CONSTRAINT member_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT member_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES member(id),
	CONSTRAINT member_revision_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id),
	CONSTRAINT member_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_member_revision_group_id ON member_revision USING btree (group_id);
CREATE INDEX idx_member_revision_id ON member_revision USING btree (id);

-- Drop table

-- DROP TABLE public.package;

CREATE TABLE public.package (
	id text NOT NULL,
	name varchar(100) NOT NULL,
	title text NULL,
	"version" varchar(100) NULL,
	url text NULL,
	notes text NULL,
	license_id text NULL,
	revision_id text NULL,
	author text NULL,
	author_email text NULL,
	maintainer text NULL,
	maintainer_email text NULL,
	state text NULL,
	"type" text NULL,
	owner_org text NULL,
	private bool NULL DEFAULT false,
	metadata_modified timestamp NULL,
	creator_user_id text NULL,
	CONSTRAINT package_name_key UNIQUE (name),
	CONSTRAINT package_pkey PRIMARY KEY (id),
	CONSTRAINT package_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_pkg_lname ON package USING btree (lower((name)::text));
CREATE INDEX ix_package_url ON package USING btree (url);

-- Drop table

-- DROP TABLE public.package_contact_information;

CREATE TABLE public.package_contact_information (
	id text NOT NULL,
	user_id text NOT NULL,
	contact_name text NULL,
	contact_mailbox text NULL,
	contact_phone_number text NULL,
	contact_page text NULL,
	contact_address text NULL,
	CONSTRAINT "DATASET_CONTACT_INFORMATION_PK" PRIMARY KEY (id),
	CONSTRAINT "FK_DATASET_CONTACT_INFORMATION_USER" FOREIGN KEY (user_id) REFERENCES "user"(id) ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public.package_extra;

CREATE TABLE public.package_extra (
	id text NOT NULL,
	package_id text NULL,
	"key" text NULL,
	value text NULL,
	revision_id text NULL,
	state text NULL,
	CONSTRAINT package_extra_pkey PRIMARY KEY (id),
	CONSTRAINT package_extra_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT package_extra_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_extra_pkg_id ON package_extra USING btree (package_id);

-- Drop table

-- DROP TABLE public.package_extra_revision;

CREATE TABLE public.package_extra_revision (
	id text NOT NULL,
	package_id text NULL,
	"key" text NULL,
	value text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	state text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	CONSTRAINT package_extra_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT package_extra_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES package_extra(id),
	CONSTRAINT package_extra_revision_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT package_extra_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_package_extra_package_id ON package_extra_revision USING btree (package_id, current);
CREATE INDEX idx_package_extra_rev_id ON package_extra_revision USING btree (revision_id);
CREATE INDEX idx_package_extra_revision ON package_extra_revision USING btree (id);
CREATE INDEX idx_package_extra_revision_pkg_id ON package_extra_revision USING btree (package_id);

-- Drop table

-- DROP TABLE public.package_relationship;

CREATE TABLE public.package_relationship (
	id text NOT NULL,
	subject_package_id text NULL,
	object_package_id text NULL,
	"type" text NULL,
	"comment" text NULL,
	revision_id text NULL,
	state text NULL,
	CONSTRAINT package_relationship_pkey PRIMARY KEY (id),
	CONSTRAINT package_relationship_object_package_id_fkey FOREIGN KEY (object_package_id) REFERENCES package(id),
	CONSTRAINT package_relationship_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id),
	CONSTRAINT package_relationship_subject_package_id_fkey FOREIGN KEY (subject_package_id) REFERENCES package(id)
);

-- Drop table

-- DROP TABLE public.package_relationship_revision;

CREATE TABLE public.package_relationship_revision (
	id text NOT NULL,
	subject_package_id text NULL,
	object_package_id text NULL,
	"type" text NULL,
	"comment" text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	state text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	CONSTRAINT package_relationship_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT package_relationship_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES package_relationship(id),
	CONSTRAINT package_relationship_revision_object_package_id_fkey FOREIGN KEY (object_package_id) REFERENCES package(id),
	CONSTRAINT package_relationship_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id),
	CONSTRAINT package_relationship_revision_subject_package_id_fkey FOREIGN KEY (subject_package_id) REFERENCES package(id)
);
CREATE INDEX idx_package_relationship_current ON package_relationship_revision USING btree (current);
CREATE INDEX idx_period_package_relationship ON package_relationship_revision USING btree (revision_timestamp, expired_timestamp, object_package_id, subject_package_id);

-- Drop table

-- DROP TABLE public.package_revision;

CREATE TABLE public.package_revision (
	id text NOT NULL,
	name varchar(100) NOT NULL,
	title text NULL,
	"version" varchar(100) NULL,
	url text NULL,
	notes text NULL,
	license_id text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	author text NULL,
	author_email text NULL,
	maintainer text NULL,
	maintainer_email text NULL,
	state text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	"type" text NULL,
	owner_org text NULL,
	private bool NULL DEFAULT false,
	metadata_modified timestamp NULL,
	creator_user_id text NULL,
	CONSTRAINT package_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT package_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES package(id),
	CONSTRAINT package_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_package_current ON package_revision USING btree (current);
CREATE INDEX idx_package_period ON package_revision USING btree (revision_timestamp, expired_timestamp, id);
CREATE INDEX idx_pkg_revision_id ON package_revision USING btree (id);
CREATE INDEX idx_pkg_revision_name ON package_revision USING btree (name);
CREATE INDEX idx_pkg_revision_rev_id ON package_revision USING btree (revision_id);

-- Drop table

-- DROP TABLE public.rating;

CREATE TABLE public.rating (
	id text NOT NULL,
	user_id text NULL,
	user_ip_address text NULL,
	package_id text NULL,
	rating float8 NULL,
	created timestamp NULL,
	CONSTRAINT rating_pkey PRIMARY KEY (id),
	CONSTRAINT rating_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT rating_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id)
);
CREATE INDEX idx_rating_id ON rating USING btree (id);
CREATE INDEX idx_rating_package_id ON rating USING btree (package_id);
CREATE INDEX idx_rating_user_id ON rating USING btree (user_id);

-- Drop table

-- DROP TABLE public.related_dataset;

CREATE TABLE public.related_dataset (
	id text NOT NULL,
	dataset_id text NOT NULL,
	related_id text NOT NULL,
	status text NULL,
	CONSTRAINT related_dataset_pkey PRIMARY KEY (id),
	CONSTRAINT related_dataset_dataset_id_fkey FOREIGN KEY (dataset_id) REFERENCES package(id),
	CONSTRAINT related_dataset_related_id_fkey FOREIGN KEY (related_id) REFERENCES related(id)
);

-- Drop table

-- DROP TABLE public.resource_group;

CREATE TABLE public.resource_group (
	id text NOT NULL,
	package_id text NULL,
	"label" text NULL,
	sort_order text NULL,
	extras text NULL,
	state text NULL,
	revision_id text NULL,
	CONSTRAINT resource_group_pkey PRIMARY KEY (id),
	CONSTRAINT resource_group_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT resource_group_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_resource_group_pkg_id ON resource_group USING btree (package_id);

-- Drop table

-- DROP TABLE public.resource_group_revision;

CREATE TABLE public.resource_group_revision (
	id text NOT NULL,
	package_id text NULL,
	"label" text NULL,
	sort_order text NULL,
	extras text NULL,
	state text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	CONSTRAINT resource_group_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT resource_group_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES resource_group(id),
	CONSTRAINT resource_group_revision_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT resource_group_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_resource_group_revision ON resource_group_revision USING btree (id);
CREATE INDEX idx_resource_group_revision_pkg_id ON resource_group_revision USING btree (package_id);
CREATE INDEX idx_resource_group_revision_rev_id ON resource_group_revision USING btree (revision_id);

-- Drop table

-- DROP TABLE public.system_info;

CREATE TABLE public.system_info (
	id serial NOT NULL,
	"key" varchar(100) NOT NULL,
	value text NULL,
	revision_id text NULL,
	CONSTRAINT system_info_key_key UNIQUE (key),
	CONSTRAINT system_info_pkey PRIMARY KEY (id),
	CONSTRAINT system_info_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);

-- Drop table

-- DROP TABLE public.system_info_revision;

CREATE TABLE public.system_info_revision (
	id serial NOT NULL,
	"key" varchar(100) NOT NULL,
	value text NULL,
	revision_id text NOT NULL,
	continuity_id int4 NULL,
	CONSTRAINT system_info_revision_key_key UNIQUE (key),
	CONSTRAINT system_info_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT system_info_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES system_info(id),
	CONSTRAINT system_info_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);

-- Drop table

-- DROP TABLE public.tag;

CREATE TABLE public.tag (
	id text NOT NULL,
	name varchar(100) NOT NULL,
	vocabulary_id varchar(100) NULL,
	CONSTRAINT tag_name_vocabulary_id_key UNIQUE (name, vocabulary_id),
	CONSTRAINT tag_pkey PRIMARY KEY (id),
	CONSTRAINT tag_vocabulary_id_fkey FOREIGN KEY (vocabulary_id) REFERENCES vocabulary(id)
);
CREATE INDEX idx_tag_id ON tag USING btree (id);
CREATE INDEX idx_tag_name ON tag USING btree (name);

-- Drop table

-- DROP TABLE public.user_following_dataset;

CREATE TABLE public.user_following_dataset (
	follower_id text NOT NULL,
	object_id text NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT user_following_dataset_pkey PRIMARY KEY (follower_id, object_id),
	CONSTRAINT user_following_dataset_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT user_following_dataset_object_id_fkey FOREIGN KEY (object_id) REFERENCES package(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public.user_following_group;

CREATE TABLE public.user_following_group (
	follower_id text NOT NULL,
	object_id text NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT user_following_group_pkey PRIMARY KEY (follower_id, object_id),
	CONSTRAINT user_following_group_group_id_fkey FOREIGN KEY (object_id) REFERENCES "group"(id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT user_following_group_user_id_fkey FOREIGN KEY (follower_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public.user_following_user;

CREATE TABLE public.user_following_user (
	follower_id text NOT NULL,
	object_id text NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT user_following_user_pkey PRIMARY KEY (follower_id, object_id),
	CONSTRAINT user_following_user_follower_id_fkey FOREIGN KEY (follower_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT user_following_user_object_id_fkey FOREIGN KEY (object_id) REFERENCES "user"(id) ON UPDATE CASCADE ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public.user_object_role;

CREATE TABLE public.user_object_role (
	id text NOT NULL,
	user_id text NULL,
	context text NOT NULL,
	"role" text NULL,
	authorized_group_id text NULL,
	CONSTRAINT user_object_role_pkey PRIMARY KEY (id),
	CONSTRAINT user_object_role_authorized_group_id_fkey FOREIGN KEY (authorized_group_id) REFERENCES authorization_group(id),
	CONSTRAINT user_object_role_user_id_fkey FOREIGN KEY (user_id) REFERENCES "user"(id)
);
CREATE INDEX idx_uor_context ON user_object_role USING btree (context);
CREATE INDEX idx_uor_id ON user_object_role USING btree (id);
CREATE INDEX idx_uor_role ON user_object_role USING btree (role);
CREATE INDEX idx_uor_user_id ON user_object_role USING btree (user_id);
CREATE INDEX idx_uor_user_id_role ON user_object_role USING btree (user_id, role);

-- Drop table

-- DROP TABLE public.authorization_group_role;

CREATE TABLE public.authorization_group_role (
	user_object_role_id text NOT NULL,
	authorization_group_id text NULL,
	CONSTRAINT authorization_group_role_pkey PRIMARY KEY (user_object_role_id),
	CONSTRAINT authorization_group_role_authorization_group_id_fkey FOREIGN KEY (authorization_group_id) REFERENCES authorization_group(id),
	CONSTRAINT authorization_group_role_user_object_role_id_fkey FOREIGN KEY (user_object_role_id) REFERENCES user_object_role(id)
);

-- Drop table

-- DROP TABLE public.group_role;

CREATE TABLE public.group_role (
	user_object_role_id text NOT NULL,
	group_id text NULL,
	CONSTRAINT group_role_pkey PRIMARY KEY (user_object_role_id),
	CONSTRAINT group_role_group_id_fkey FOREIGN KEY (group_id) REFERENCES "group"(id),
	CONSTRAINT group_role_user_object_role_id_fkey FOREIGN KEY (user_object_role_id) REFERENCES user_object_role(id)
);

-- Drop table

-- DROP TABLE public.package_role;

CREATE TABLE public.package_role (
	user_object_role_id text NOT NULL,
	package_id text NULL,
	CONSTRAINT package_role_pkey PRIMARY KEY (user_object_role_id),
	CONSTRAINT package_role_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT package_role_user_object_role_id_fkey FOREIGN KEY (user_object_role_id) REFERENCES user_object_role(id)
);

-- Drop table

-- DROP TABLE public.package_tag;

CREATE TABLE public.package_tag (
	id text NOT NULL,
	package_id text NULL,
	tag_id text NULL,
	revision_id text NULL,
	state text NULL,
	CONSTRAINT package_tag_pkey PRIMARY KEY (id),
	CONSTRAINT package_tag_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT package_tag_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id),
	CONSTRAINT package_tag_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tag(id)
);
CREATE INDEX idx_package_tag_pkg_id ON package_tag USING btree (package_id);
CREATE INDEX idx_package_tag_pkg_id_tag_id ON package_tag USING btree (tag_id, package_id);
CREATE INDEX idx_package_tag_tag_id ON package_tag USING btree (tag_id);

-- Drop table

-- DROP TABLE public.package_tag_revision;

CREATE TABLE public.package_tag_revision (
	id text NOT NULL,
	package_id text NULL,
	tag_id text NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	state text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	CONSTRAINT package_tag_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT package_tag_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES package_tag(id),
	CONSTRAINT package_tag_revision_package_id_fkey FOREIGN KEY (package_id) REFERENCES package(id),
	CONSTRAINT package_tag_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id),
	CONSTRAINT package_tag_revision_tag_id_fkey FOREIGN KEY (tag_id) REFERENCES tag(id)
);
CREATE INDEX idx_package_tag_revision_id ON package_tag_revision USING btree (id);
CREATE INDEX idx_package_tag_revision_pkg_id ON package_tag_revision USING btree (package_id);
CREATE INDEX idx_package_tag_revision_rev_id ON package_tag_revision USING btree (revision_id);
CREATE INDEX idx_package_tag_revision_tag_id ON package_tag_revision USING btree (tag_id);

-- Drop table

-- DROP TABLE public.resource;

CREATE TABLE public.resource (
	id text NOT NULL,
	resource_group_id text NULL,
	url text NOT NULL,
	format text NULL,
	description text NULL,
	"position" int4 NULL,
	revision_id text NULL,
	hash text NULL,
	state text NULL,
	extras text NULL,
	name text NULL,
	resource_type text NULL,
	mimetype text NULL,
	mimetype_inner text NULL,
	"size" int8 NULL,
	last_modified timestamp NULL,
	cache_url text NULL,
	cache_last_updated timestamp NULL,
	webstore_url text NULL,
	webstore_last_updated timestamp NULL,
	created timestamp NULL,
	url_type text NULL,
	resource_count int8 NULL DEFAULT 0,
	CONSTRAINT resource_pkey PRIMARY KEY (id),
	CONSTRAINT resource_resource_group_id_fkey FOREIGN KEY (resource_group_id) REFERENCES resource_group(id),
	CONSTRAINT resource_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_package_resource_id ON resource USING btree (id);
CREATE INDEX idx_package_resource_pkg_id ON resource USING btree (resource_group_id);
CREATE INDEX idx_package_resource_url ON resource USING btree (url);
CREATE INDEX idx_resource_name ON resource USING btree (name);

-- Drop table

-- DROP TABLE public.resource_revision;

CREATE TABLE public.resource_revision (
	id text NOT NULL,
	resource_group_id text NULL,
	url text NOT NULL,
	format text NULL,
	description text NULL,
	"position" int4 NULL,
	revision_id text NOT NULL,
	continuity_id text NULL,
	hash text NULL,
	state text NULL,
	extras text NULL,
	expired_id text NULL,
	revision_timestamp timestamp NULL,
	expired_timestamp timestamp NULL,
	"current" bool NULL,
	name text NULL,
	resource_type text NULL,
	mimetype text NULL,
	mimetype_inner text NULL,
	"size" int8 NULL,
	last_modified timestamp NULL,
	cache_url text NULL,
	cache_last_updated timestamp NULL,
	webstore_url text NULL,
	webstore_last_updated timestamp NULL,
	created timestamp NULL,
	url_type text NULL,
	CONSTRAINT resource_revision_pkey PRIMARY KEY (id, revision_id),
	CONSTRAINT resource_revision_continuity_id_fkey FOREIGN KEY (continuity_id) REFERENCES resource(id),
	CONSTRAINT resource_revision_resource_group_id_fkey FOREIGN KEY (resource_group_id) REFERENCES resource_group(id),
	CONSTRAINT resource_revision_revision_id_fkey FOREIGN KEY (revision_id) REFERENCES revision(id)
);
CREATE INDEX idx_package_resource_rev_id ON resource_revision USING btree (revision_id);
CREATE INDEX idx_resource_resource_group_id ON resource_revision USING btree (resource_group_id, current);
CREATE INDEX idx_resource_revision ON resource_revision USING btree (id);

-- Drop table

-- DROP TABLE public.resource_term_translation;

CREATE TABLE public.resource_term_translation (
	id text NOT NULL,
	resource_id text NOT NULL,
	resource_revision_id text NOT NULL,
	field text NOT NULL,
	field_translation text NOT NULL,
	lang_code text NOT NULL,
	CONSTRAINT "RESOURCE_TERM_TRANSLATION_PK" PRIMARY KEY (id),
	CONSTRAINT "UNIQUE_KEY" UNIQUE (resource_id, resource_revision_id, field, lang_code),
	CONSTRAINT "FK_RESOURCE_ID" FOREIGN KEY (resource_id) REFERENCES resource(id) ON DELETE CASCADE,
	CONSTRAINT "FK_REVISION_ID" FOREIGN KEY (resource_revision_id) REFERENCES revision(id) ON DELETE CASCADE
);

-- Drop table

-- DROP TABLE public.system_role;

CREATE TABLE public.system_role (
	user_object_role_id text NOT NULL,
	CONSTRAINT system_role_pkey PRIMARY KEY (user_object_role_id),
	CONSTRAINT system_role_user_object_role_id_fkey FOREIGN KEY (user_object_role_id) REFERENCES user_object_role(id)
);
