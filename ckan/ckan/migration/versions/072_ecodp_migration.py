import logging

log = logging.getLogger("ckan") #Use the standard logger from ckan

def upgrade(migrate_engine):
    fix_ecportal_migration = '''
            BEGIN;
            
            UPDATE public."group"
            SET is_organization = true
             WHERE "group".type = 'organization';
            
            UPDATE public."group_revision"
            SET is_organization = true
             WHERE "group_revision".type = 'organization';
            
            
            UPDATE package SET owner_org = x.group_id FROM (select  package.revision_id, member.group_id FROM package JOIN member ON package.revision_id = member.revision_id) x WHERE package.revision_id = x.revision_id;
            
            UPDATE package_revision SET owner_org = x.group_id FROM (select  package_revision.revision_id, member.group_id FROM package_revision JOIN member ON package_revision.revision_id = member.revision_id) x WHERE package_revision.revision_id = x.revision_id;
            
            COMMIT;
            '''
    
    migrate_engine.execute(fix_ecportal_migration)
