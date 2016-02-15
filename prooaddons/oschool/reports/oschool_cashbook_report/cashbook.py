# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class cashbook_wizard(models.Model):
    _name = 'oschool.cashbook.wizard'


    def _default_user_ids(self, cr, uid, context=None):
        company_id =self.pool.get("res.users").browse(cr, uid, uid).company_id.id
        user_ids = self.pool.get("res.users").search(cr, uid, [])
        ids = []
        for user in self.pool.get("res.users").browse(cr, uid, user_ids):
            if user.pos_config:
                ids.append(user.id)
        return ids



    date_start = fields.Date( string="Date de début")
    date_stop = fields.Date( string="Date de fin")
    checkout_wizard = fields.Many2many('res.users', 'checkout_wizard_rel', 'partner_id', 'schedule_id', string='Caissiers')
    #domain="[('school_product_type', '=', 'transport')

    _defaults = {
        'date_start':datetime.today(),
        'date_stop':datetime.today(),
        'checkout_wizard': _default_user_ids,
    }




    def print_report(self, cr, uid,ids, context=None):
        vals = {}
        vals['date_start'] = context.get('date_start')
        vals['date_stop'] = context.get('date_stop')
        vals['checkout_wizard'] = context.get('checkout_wizard')
        report_ids = [self.create(cr, uid, vals)]

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.report_cashbook',
            'datas': {
                    'model':'oschool.cashbook.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-pdf'
                },
            'nodestroy': True
            }