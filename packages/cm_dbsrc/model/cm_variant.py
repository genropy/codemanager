# encoding: utf-8
from gnr.core.gnrdecorator import public_method
from gnr.app.gnrapp import GnrApp

class Table(object):
    def config_db(self,pkg):
        tbl=pkg.table('cm_variant', pkey='code', name_long='Variants', name_plural='Variants',caption_field='name')
        self.sysFields(tbl,id=False)
        tbl.column('code',size=':30',name_long='VariantCode')
        tbl.column('project_code', size=':20', name_long='ProjectCode'
                        ).relation('cm_project.code',relation_name='variants',
                                    onDelete='cascade',mode='foreignkey')
        tbl.column('name', size=':40', name_long='VariantName')

    @public_method
    def importPackages(self,variant_code=None,project_code=None,filterpkg=None,import_mode=None):
        pkgtblobj = self.db.table('cm_dbsrc.cm_pkg')
        db = GnrApp(variant_code).db
        filterpkg = filterpkg or db.packages.keys()
        cm_table = self.db.table('cm_dbsrc.cm_table')

        for pkgid,pkgobj in db.packages.items():
            if pkgid not in filterpkg:
                continue
            with pkgtblobj.recordToUpdate(insertMissing=True,cm_variant=variant_code,cm_project=project_code,code=pkgid) as pkgrecord:
                pkgrecord['description'] = pkgobj.attributes.get('name_long')
                pkgrecord['cm_variant'] = variant_code
                pkgrecord['cm_project'] = project_code
            for tblobj in pkgobj.tables.values():
                cm_table.importTable(pkgrecord['id'], tblobj, import_mode=import_mode)
            self.db.commit()
            
        #for tblobj in pkg.tables.values():
        #    cm_table.importTable(pkg_id, tblobj, import_mode=import_mode)