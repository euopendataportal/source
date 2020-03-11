import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    change_eurovoc_domains_type = '''
            BEGIN;

            ALTER TABLE public.resource_term_translation
            DROP CONSTRAINT "FK_RESOURCE_ID",
            ADD CONSTRAINT "FK_RESOURCE_ID" FOREIGN KEY (resource_id)
                              REFERENCES resource (id) MATCH SIMPLE
                              ON UPDATE NO ACTION ON DELETE CASCADE,
            DROP CONSTRAINT "FK_REVISION_ID",
            ADD CONSTRAINT "FK_REVISION_ID" FOREIGN KEY (resource_revision_id)
                              REFERENCES revision (id) MATCH SIMPLE
                              ON UPDATE NO ACTION ON DELETE CASCADE
            ;

            COMMIT;
            '''

    migrate_engine.execute(change_eurovoc_domains_type)
