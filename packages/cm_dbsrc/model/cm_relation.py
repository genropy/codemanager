# encoding: utf-8

from gnr.core.gnrbag import Bag

class Table(object):
    def config_db(self,pkg):
        tbl =  pkg.table('cm_relation',
                        pkey='id',
                        name_long='Relation',
                        name_plural='Relations',
                        partition_cm_variant='cm_variant',
                        caption_field='name')
        self.sysFields(tbl)
        tbl.column('cm_variant',size=':30', group='_', name_long='Variant'
                    ).relation('cm_variant.code', relation_name='variant_relations', mode='foreignkey', onDelete='raise')
        tbl.column('relation_column' ,name_long='Relation column').relation('cm_column.full_name',
                                                                            relation_name='from_relations', 
                                                                            meta_thmode='plain')
        tbl.column('related_column', name_long='Related column').relation('cm_column.full_name',
                                                                           relation_name='to_relations',  
                                                                           meta_thmode='plain')
        tbl.column('rel_name',  name_long='Relation name')
        tbl.column('rel_mode',  name_long='Relation mode')
        tbl.column('rel_on_delete',  name_long='onDelete')

    def importRelation(self, column_name, relation_name=None,  related_column=None, mode=None, onDelete=None, **kwargs):
        self.deleteSelection(where='$relation_column=:column_name', column_name=column_name)
        sr = related_column.split('.')
        if len(sr) == 2:
            related_column='{pkg}.{related_column}'.format(pkg = column_name.split('.')[0], related_column=related_column)
        rel_record = self.newrecord(relation_column = column_name, 
                          rel_name = relation_name,
                          rel_mode = mode,
                          related_column=related_column, 
                          rel_on_delete=onDelete)
        self.insert(rel_record)
