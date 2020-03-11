import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    add_mapping_table = '''
            BEGIN;

            CREATE TABLE dataset_id_mapping
            (
              external_id    TEXT              NOT NULL
                CONSTRAINT external_id_pkey
                PRIMARY KEY,
              internal_id TEXT not null,
              publisher TEXT not null 
            );
            
            CREATE UNIQUE INDEX dataset_id_mapping_internal_id_uindex
              ON dataset_id_mapping (internal_id);
            CREATE INDEX dataset_id_mapping_publisher_index
              ON dataset_id_mapping (publisher);


            COMMIT;

            '''

    migrate_engine.execute(add_mapping_table)
