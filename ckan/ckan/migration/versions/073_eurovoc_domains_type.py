import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    change_eurovoc_domains_type = '''
            BEGIN;

            update "group" set type='eurovoc_domain' where type = 'group';
            
            COMMIT;
            '''

    migrate_engine.execute(change_eurovoc_domains_type)
