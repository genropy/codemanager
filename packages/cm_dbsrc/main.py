#!/usr/bin/env python
# encoding: utf-8
from gnr.app.gnrdbo import GnrDboTable, GnrDboPackage

class Package(GnrDboPackage):
    def config_attributes(self):
        return dict(comment='Db model src', sqlschema='cm_dbsrc',sqlprefix=True,
                    name_short='Db model src', name_long='Db model src analyzer')
                    
    def config_db(self, pkg):
        pass
        
class Table(GnrDboTable):
    pass
