#!/usr/bin/python3
# -*- coding: utf-8 -*-
class Menu(object):
    def config(self,root):
        cm_dbsrc = root.branch('Db analysis')
        cm_dbsrc.thpage('Projects',table='cm_dbsrc.cm_project')
        cm_dbsrc.thpage('ProjectVariants',table='cm_dbsrc.cm_variant')
        cm_dbsrc.thpage('Packages',table='cm_dbsrc.cm_pkg')
        cm_dbsrc.thpage('Tables',table='cm_dbsrc.cm_table')
        cm_dbsrc.thpage('Columns',table='cm_dbsrc.cm_column')