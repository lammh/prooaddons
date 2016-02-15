# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions
from openerp.addons.oschool import tools

import logging
_logger = logging.getLogger(__name__)

class cashbook_wizard(models.Model):
    _name = 'oschool.payment.wizard'

    period_id = fields.Many2one('account.period', string="period", required=True)
    academic_year_id = fields.Many2one('oschool.academic_year', 'Academic year', required=True)

    def default_academic_year(self, cr, uid, context):
        year_obj = self.pool.get('oschool.academic_year')
        year_id = year_obj.search(cr, uid,[
                                         ('state','=', 'current'),
                                            ('company_id','=',tools.get_default_company(self,cr,uid))
                                         ])
        if year_id:
            return  year_id[0]
        else:
            return False
    def onchange_period(self, cr, uid, ids, academic_year_id):
        if academic_year_id:
            academic_year = self.pool.get('oschool.academic_year').browse(cr, uid, academic_year_id)
            periods = []
            for period in academic_year.period_ids:
                periods.append(period.id)
            res = {'value': {}, 'domain':{'period_id':[('id','in',periods)]}}
        return res
    _defaults = {
                 'academic_year_id' : lambda self, cr, uid, context: self.default_academic_year(cr, uid, context)
                }

    def print_report(self, cr, uid,ids, context=None):
        vals = {}
        vals['academic_year_id'] = context.get('academic_year_id')
        vals['period_id'] = context.get('period_id')
        report_ids = [self.create(cr, uid, vals)]

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.payment_report',
            'datas': {
                    'model':'oschool.payment.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-pdf'
                },
            'nodestroy': True
            }