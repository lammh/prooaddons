# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, exceptions
from openerp.osv import osv
from openerp import fields
from openerp.tools.translate import _
import calendar
import openerp.addons.decimal_precision as dp

class pos_line_update(osv.osv_memory):
    _name = "oschool.study.update"
    _description = "Update Study"

    subscriber = fields.Boolean("Subscriber")
    discount_study = fields.Float('Discount', digits_compute=dp.get_precision('Discount'))



    def move_line(self, cr, uid, ids, context):
        pos_line_obj = self.pool.get('pos.order.line')
        line_id = context.get('active_id')
        old_line = pos_line_obj.browse(cr, uid, line_id)
        data = self.browse(cr, uid, ids, context=context)[0]
        pos_line_obj.write(cr, uid, old_line.id, {'subscriber': data.subscriber, 'discount': data.discount_study})

        return {'type': 'ir.actions.act_window_close'}

class account_invoice_confirm(osv.osv_memory):
    _name = "oschool.study.generate"
    _description = "Study Generate"

    def study_generate(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        active_ids = context.get('active_ids', []) or []

        proxy = self.pool['res.partner']
        for record in proxy.browse(cr, uid, active_ids, context=context):
            if not record.academic_year_id:
                raise osv.except_osv(_('Warning!'), _("Student %s don't have academic year.")%(record.display_name,))
            if record.academic_year_id.state != 'current':
                raise osv.except_osv(_('Warning!'), _("Academic year %s is not current.")%(record.academic_year_id.name,))
            record.study_student()

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
