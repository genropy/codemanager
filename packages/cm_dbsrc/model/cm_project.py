# encoding: utf-8

from gnr.app.gnrdeploy import PathResolver
from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('cm_project', pkey='code', name_long='Project', name_plural='Projects',caption_field='name')
        self.sysFields(tbl,id=False)
        tbl.column('code', size=':10', name_long='ProjectCode',validate_notnull=True)
        tbl.column('name', size=':40', name_long='ProjectDescription')
        #tbl.column('repository_code',size='22', group='_', name_long=''
        #            ).relation('', relation_name='', mode='foreignkey', onDelete='raise')
    

    def trigger_onInserted(self,record):
        p = PathResolver()
        projectpath = p.project_name_to_path(record['code'])
        project_node = self.db.application.site.storageNode(projectpath)
        project_code = record['code']
        if not project_node.exists:
            return
        instance_folder_node = project_node.child('instances')
        if not instance_folder_node.exists:
            return
        cm_variant_tblobj = self.db.table('cm_dbsrc.cm_variant')
        for instanceNode in instance_folder_node.children():
            if instanceNode.isdir:
                instance_code = instanceNode.basename
                cm_variant_tblobj.insert(
                    cm_variant_tblobj.newrecord(code=instance_code,name=instance_code,project_code=project_code)
                )
        

