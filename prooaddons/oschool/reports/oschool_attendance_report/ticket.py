# -*- coding: utf-8 -*-
from openerp import fields, models, api, exceptions
from datetime import datetime, timedelta

import logging
_logger = logging.getLogger(__name__)

class canteen_wizard(models.Model):
    _name = 'oschool.ticket.wizard'

    class_id = fields.Many2one('oschool.classes', string="Zone")
    period_id = fields.Many2one('account.period', 'Period')
    month = fields.Char(compute="_get_month")
    presence_ids = fields.Many2many('res.partner')

    @api.one
    @api.depends('period_id')
    def _get_month(self):
        self.month = datetime.strptime( self.period_id.date_start, "%Y-%m-%d").strftime("%B")
    def create(self, cr, uid, vals):
        presence_obj = self.pool.get('res.partner')
        academic_year_obj = self.pool.get('oschool.academic_year')
        academic_year_id = academic_year_obj.search(cr, uid, [
            ('state', '=', 'current'),
        ])
        if academic_year_id:
            presence_ids = presence_obj.search(cr, uid, [
                ('class_id', '=', vals['class_id']),
                ('academic_year_id', '=', academic_year_id),
            ])
            canteen_obj = self.pool.get('oschool.canteen.wizard')
            canteen_ids = [canteen_obj.create(cr, uid, vals)]
            canteen = canteen_obj.browse(cr, uid, canteen_ids)

            restaurant_obj = self.pool.get('oschool.restaurant.wizard')
            restaurant_ids = [restaurant_obj.create(cr, uid, vals)]
            restaurant = restaurant_obj.browse(cr, uid, restaurant_ids)

            res = []
            for presence in canteen.presence_ids:
                res.append(presence.student_id.id)
            for presence in restaurant.presence_ids:
                res.append(presence.student_id.id)

            presence_ids = list(set(presence_ids) - set(res))
            r = []
            for id in presence_ids:
                r.append([4,id])
            vals['presence_ids'] = r
        return  super(canteen_wizard, self).create(cr, uid, vals)