import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    add_resource_count_table = '''
            BEGIN;

            CREATE TABLE resource_download_count
            (
              resource_id    TEXT              NOT NULL
                CONSTRAINT resource_download_count_pkey
                PRIMARY KEY,
              resource_count INTEGER DEFAULT 0 NOT NULL,
	          dataset_id text default ''::text not null
            );
            
            CREATE UNIQUE INDEX resource_download_count_resource_id_uindex
              ON resource_download_count (resource_id);


            COMMIT;
            '''

    adapt_trecking_summary = '''
    BEGIN;
    update tracking_summary
      set package_id = regexp_replace(url, '^.*/', 'http://data.europa.eu/88u/dataset/')
      where tracking_type = 'page' and url like '%/dataset/%' and url not like '%/resource%';
      
    COMMIT;
    '''

    migrate_engine.execute(add_resource_count_table)
    migrate_engine.execute(adapt_trecking_summary)
