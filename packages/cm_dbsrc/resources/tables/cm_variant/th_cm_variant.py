#!/usr/bin/python3
# -*- coding: utf-8 -*-

from gnr.web.gnrbaseclasses import BaseComponent

class View(BaseComponent):

    def th_struct(self,struct):
        r = struct.view().rows()
        r.fieldcell('project_code')
        r.fieldcell('code')

        r.fieldcell('name')

    def th_order(self):
        return 'code'

    def th_query(self):
        return dict(column='code', op='contains', val='')



class Form(BaseComponent):

    def th_form(self, form):
        bc = form.center.borderContainer()
        fb = bc.contentPane(region='top',datapath='.record').formbuilder(cols=2, border_spacing='4px')
        fb.field('project_code')
        fb.field('code')
        fb.field('name',colspan=2,width='100%')
        fb.button('Import packages').dataRpc(self.db.table('cm_dbsrc.cm_variant').importPackages,variant_code='=.code',project_code='=.project_code')
        bc.contentPane(region='center').dialogTableHandler(
            relation='@packages',addrow=False,delrow=False
        )


    def th_options(self):
        return dict(dialog_parentRatio=.9)
