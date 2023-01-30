# encoding: utf-8

import os
from gnr.core.gnrdecorator import public_method
from gnr.core import gnrlist


class Table(object):
    def config_db(self, pkg):
        tbl =  pkg.table('cm_table',
                        pkey='id', name_long='Legacy table',
                        name_plural='Legacy tables',
                        caption_field='sqlname')
        self.sysFields(tbl)
        tbl.column('pkg_id',size='22', name_long='Package').relation('cm_pkg.id',
                                                            relation_name='cm_tables', 
                                                            mode='foreignkey',
                                                            onDelete='cascade',
                                                            meta_thmode='dialog')
        tbl.column('name',name_long='Name', indexed=True)
        tbl.column('primary_key',name_long='Pkey', indexed=True)
        tbl.column('sqlname', name_long='SqlName', indexed=True)
        tbl.column('description',name_long='Description', indexed=True)
        tbl.column('notes', name_long='Notes')
        tbl.column('group', name_long='Group', batch_assign=True)
    
        tbl.column('multidb', name_long='Multi DB', values='*:Replicated on all databases,one:Replicated on one specific database,true:Only subscripted records')
        tbl.aliasColumn('legacy_db','@pkg_id.legacy_db',static=True)
        tbl.aliasColumn('legacy_schema','@pkg_id.legacy_schema',static=True)
        tbl.aliasColumn('pkg','@pkg_id.code',static=True)
        tbl.aliasColumn('cm_variant','@pkg_id.cm_variant',static=True)

    @public_method
    def importTable(self, pkg_id=None,  tblobj=None, import_mode=None):
        tbl_record = self.newrecord(pkg_id = pkg_id,
                           name=tblobj.name,
                           sqlname = tblobj.sqlname,
                           description=tblobj.name_long)
        cm_variant = self.db.table('cm_dbsrc.cm_pkg').readColumns(columns='$cm_variant',pkey=pkg_id)
        existing = self.query(where='$sqlname=:sqlname',
                                for_update=True,
                                sqlname=tblobj.sqlname).fetch()
        if not existing:
            self.insert(tbl_record)
        else:
            old_tbl_record = dict(existing[0])
            if import_mode == 'restart':
                self.delete(old_tbl_record)
                self.insert(tbl_record)
            elif import_mode == 'update':
                tbl_record['id'] = old_tbl_record['id']
                self.update(tbl_record, old_tbl_record)
            else:
                tbl_record=old_tbl_record

        for col_obj in tblobj.columns.values():
            self.db.table('cm_dbsrc.cm_column').importColumn(tbl_record['id'], col_obj, import_mode=None,cm_variant=cm_variant)
            

    @public_method(caption='Import columns and relations')
    def actionMenu_importColumns(self,pkey=None,selectedPkeys=None,**kwargs):
        selectedPkeys = selectedPkeys or [pkey]
        f = self.query(where='$id IN :selectedPkeys',selectedPkeys=selectedPkeys).fetch()
        legacy_db = f[0]['legacy_db']
        legacy_schema = f[0]['legacy_schema']
        if not legacy_db:
            return
        extdb = self.db.table('cm_dbsrc.cm_pkg').getLegacyDb(legacy_db)
        tblpkeys = []
        cm_variant = f[0]['cm_variant']
        for tbl in f:
            self._importColumnsFromTbl(extdb,legacy_schema,tbl)
            tblpkeys.append(tbl['id'])
        cm_rel_tbl = self.db.table('cm_dbsrc.cm_relation')
        cm_columns = self.db.table('cm_dbsrc.cm_column').query(where='$table_id IN :tblpkeys',
                                                            tblpkeys=tblpkeys).fetchAsDict('full_name')
        relations = extdb.adapter.relations()

        for (many_rel_name, many_schema, many_table, 
            many_cols, one_rel_name, one_schema, 
            one_table, one_cols, upd_rule, 
            del_rule, init_defer) in relations:
            many_field = many_cols[0]
            one_field = one_cols[0]
            column = f'{many_schema}.{many_table}.{many_field}'
            related_column = f'{one_schema}.{one_table}.{one_field}'
            if column in cm_columns and related_column in cm_columns:
                rel_record = cm_rel_tbl.newrecord(relation_column = column, 
                                related_column=related_column,
                                cm_variant=cm_variant)
                cm_rel_tbl.insert(rel_record)
        self.db.commit()
    
    def _importColumnsFromTbl(self,extdb,legacy_schema,tbl):
        tbl_name = tbl['name']
        columns = list(extdb.adapter.getColInfo(schema=legacy_schema, table=tbl_name)) 
        gnrlist.sortByItem(columns, 'position')
        cm_column = self.db.table('cm_dbsrc.cm_column')
        cm_column.deleteSelection('table_id',tbl['id'])
        for col_dict in columns:
            col_dict.pop('position')
            colname = col_dict.pop('name')
            length = col_dict.pop('length', 0)
            decimals = col_dict.pop('decimals', 0)
            dtype = col_dict['dtype']
            if dtype == 'A':
                col_dict['size'] = '0:%s' % length
            elif dtype == 'C':
                col_dict['dtype'] = 'A'
                col_dict['size'] = length
            cm_column.insert(cm_column.newrecord(name=colname,data_type=col_dict['dtype'],
                                                full_name=f'{legacy_schema}.{tbl_name}.{colname}',
                                                table_id=tbl['id']))


