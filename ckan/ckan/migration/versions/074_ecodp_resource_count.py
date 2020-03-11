import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    change_eurovoc_domains_type = '''
            BEGIN;

            ALTER TABLE resource ADD COLUMN resource_count bigint DEFAULT 0;
            
            COMMIT;
            '''

    migrate_engine.execute(change_eurovoc_domains_type)
