import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    change_package_contact_information = '''
            BEGIN;

            ALTER TABLE public.package_contact_information
            DROP CONSTRAINT "FK_DATASET_CONTACT_INFORMATION_USER",
            ADD CONSTRAINT "FK_DATASET_CONTACT_INFORMATION_USER" FOREIGN KEY (user_id)
                  REFERENCES "user" (id) MATCH SIMPLE
                  ON UPDATE NO ACTION ON DELETE CASCADE;
            COMMIT;
            '''

    migrate_engine.execute(change_package_contact_information)
