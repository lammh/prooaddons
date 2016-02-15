# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class canteen_wizard(models.Model):
    _name = 'oschool.canteen.wizard'

    class_id = fields.Many2one('oschool.classes', string="Zone")
    period_id = fields.Many2one('account.period', 'Period')
    month = fields.Char(compute="_get_month")
    presence_ids = fields.One2many('oschool.student_canteen_presence','report_id')

    @api.one
    @api.depends('period_id')
    def _get_month(self):
        self.month = datetime.strptime( self.period_id.date_start, "%Y-%m-%d").strftime("%B")
    def create(self, cr, uid, vals):
        presence_obj = self.pool.get('oschool.student_canteen_presence')
        presence_ids = presence_obj.search(cr, uid, [
            ('class_id', '=', vals['class_id']),
            ('period_id', '=', vals['period_id']),
            ('day_num', '=', 1),
        ])
        r = []
        for id in presence_ids:
            r.append([4,id])
        vals['presence_ids'] = r
        return  super(canteen_wizard, self).create(cr, uid, vals)