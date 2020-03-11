import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    alter_create_contact_info_table = '''
            BEGIN;

             CREATE TABLE package_contact_information
            (
              id text NOT NULL,
              user_id text NOT NULL,
              contact_name TEXT ,
              contact_mailbox TEXT ,
              contact_phone_number TEXT ,
              contact_page TEXT ,
              contact_address TEXT,
              CONSTRAINT "DATASET_CONTACT_INFORMATION_PK" PRIMARY KEY (id),
              CONSTRAINT "FK_DATASET_CONTACT_INFORMATION_USER" FOREIGN KEY (user_id)
                  REFERENCES "user" (id) MATCH SIMPLE
                  ON UPDATE NO ACTION ON DELETE NO ACTION
                  );

            COMMIT;
            '''

    migrate_engine.execute(alter_create_contact_info_table)
