# encoding: utf-8

from gnr.core.gnrdecorator import public_method
from gnr.sql.gnrsql import GnrSqlDb
from gnr.app.gnrapp import GnrApp

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('cm_pkg',pkey='id',
                    name_long='Package',name_plural='Packages',caption_field='code')
        self.sysFields(tbl)
        
        tbl.column('code',size=':15',name_long='Code')
        tbl.column('name', name_long='Name')
        tbl.column('legacy_db',name_long='Legacy db')
        tbl.column('legacy_schema',name_long='Legacy schema')
        tbl.column('cm_project',size=':20',name_long='Cm Project').relation('cm_project.code',mode='foreignkey',
                    relation_name='pkgvariants')
        tbl.column('cm_variant',size=':30',name_long='Cm variant').relation('cm_variant.code',
                        mode='foreignkey',
                        relation_name='packages')
        tbl.column('description',name_long='Description')

    @public_method
    def importPackage(self, pkg_code=None,legacy_schema=None, import_mode=None,legacy_db=None,pkg_id=None):
        if legacy_db and legacy_db is not True:
            self.importFromLegacyDb(legacy_db,pkg_code=pkg_code,legacy_schema=legacy_schema)
            return
        cm_variant = self.readColumns(columns='$cm_variant',pkey=pkg_id)
        sourcedb = GnrApp(cm_variant).db if cm_variant else self.db
        pkg = sourcedb.package(pkg_code)
        cm_table = self.db.table('cm_dbsrc.cm_table')
        cm_col = self.db.table('cm_dbsrc.cm_column')
        if import_mode == 'restart':
            cm_table.deleteSelection(where='$pkg_id=:pkg_id', pkg_id=pkg_id)
        for tblobj in pkg.tables.values():
            cm_table.importTable(pkg_id, tblobj, import_mode=import_mode)

    def importFromLegacyDb(self,legacy_db,pkg_code,legacy_schema=None):
        externaldb = self.getLegacyDb(legacy_db)
        schemadata = externaldb.adapter.listElements('schemata')
        cm_table = self.db.table('cm_dbsrc.cm_table')
        
        for schema in schemadata:
            if legacy_schema!=schema:
                continue
            tables = externaldb.adapter.listElements('tables', schema=schema)
            for tbl in tables:
                primary_key = externaldb.adapter.getPkey(schema=legacy_schema, table=tbl)
                cm_table.insert(cm_table.newrecord(cm_pkg=pkg_code,primary_key=primary_key,
                                            name=tbl,sqlname='{}.{}'.format(schema,tbl)))
            return

    def getLegacyDb(self,legacy_db):
        connection_params = self.db.application.config['legacy_db'].getAttr(legacy_db)
        dbname=connection_params['dbname'] or connection_params['filename']
        if connection_params['implementation']!='sqlite':
            connection_params['host'] = connection_params['host'] or 'localhost'
        return GnrSqlDb(implementation=connection_params['implementation'],
                            dbname=dbname,
                            host=connection_params['host'],user=connection_params['user'],
                            password = connection_params['password'],
                            port=connection_params['port'])

