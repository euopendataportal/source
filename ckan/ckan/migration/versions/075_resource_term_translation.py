import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    change_eurovoc_domains_type = '''
            BEGIN;

            CREATE TABLE resource_term_translation
            (
              id text NOT NULL,
              resource_id text NOT NULL,
              resource_revision_id text NOT NULL,
              field text NOT NULL,
              field_translation text NOT NULL,
              lang_code text NOT NULL,
              CONSTRAINT "RESOURCE_TERM_TRANSLATION_PK" PRIMARY KEY (id),
              CONSTRAINT "FK_RESOURCE_ID" FOREIGN KEY (resource_id)
                  REFERENCES resource (id) MATCH SIMPLE
                  ON UPDATE NO ACTION ON DELETE NO ACTION,
              CONSTRAINT "FK_REVISION_ID" FOREIGN KEY (resource_revision_id)
                  REFERENCES revision (id) MATCH SIMPLE
                  ON UPDATE NO ACTION ON DELETE NO ACTION,
              CONSTRAINT "UNIQUE_KEY" UNIQUE (resource_id, resource_revision_id, field, lang_code)
            )
            WITH (
              OIDS=FALSE
            );
            ALTER TABLE resource_term_translation
              OWNER TO ecodp;

            COMMIT;
            '''

    migrate_engine.execute(change_eurovoc_domains_type)
