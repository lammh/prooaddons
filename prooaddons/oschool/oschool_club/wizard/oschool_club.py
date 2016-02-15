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
from openerp.addons.oschool import tools
import openerp.addons.decimal_precision as dp

class oschool_club_generate(osv.osv_memory):
    _name = "oschool.club.generate"
    _description = "Generate Club"

    def onchange_club(self, cr, uid, ids, club_id, context):
        if not club_id:
            return {}
        student_id = context.get('active_id')
        student = self.pool.get('res.partner').browse(cr, uid, student_id)
        if context.get('academic_year_id'):
            pos_line_obj = self.pool.get('pos.order.line')
            exist = []
            data = []
            for service in self.pool.get('pos.category').browse(cr, uid, club_id).services_ids:
                id = self.pool.get('account.period').search(cr, uid, [
                    ('code', '=', service.subscription_month),
                    ('company_id','=',tools.get_default_company(self,cr,uid)),
                    ('date_stop', '>=', student.date),
                ])
                data.append(self.pool.get('account.period').browse(cr, uid, id))
            data = sorted( list( set( data ) ),key=lambda data: data[0].date_start )

            for x in self.pool.get('pos.order.line').search(cr, uid, [('product_id.pos_categ_id', '=', club_id), ('student_id', '=', student.id), ('subscriber', '=', True)]):
                exist.append(pos_line_obj.browse(cr, uid, x).period_id.id)
            return {'value': {'period_ids': [(6, 0, [x.id not in exist and x.state == 'draft' and x.id for x in data])]}}
        return {}

    @api.model
    def _default_periods(self):
        if self._context.get('academic_year_id'):
            data = self.env['oschool.academic_year'].browse(self._context.get('academic_year_id'))
            return [(6, 0, [x.state == 'draft' and x.id for x in data.period_ids])]
        else:
            return []

    club_id = fields.Many2one('pos.category', 'Club', required=True, select=True, domain="[('school_product_type', '=', 'club'), ('academic_year', '=', context.get('academic_year_id'))]")
    period_ids = fields.Many2many('account.period', 'club_student_generate_rel', 'club_id', 'period_id', string='Periods', default=_default_periods, domain="[('state', '=', 'draft'), ('special', '=', False)]")
    discount = fields.Float('Discount', digits=dp.get_precision('Discount'))

    def generate(self, cr, uid, ids, context=None):
        category_obj = self.pool.get('pos.category')
        pos_line_obj = self.pool.get('pos.order.line')
        pos_line_obj = self.pool.get('pos.order.line')
        data = self.browse(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.product')
        for student in self.pool.get('res.partner').browse(cr, uid, context.get('active_id'), context=context):
            for period in data.period_ids:
                for product_tmpl in data.club_id.services_ids:
                    if product_tmpl.subscription_month == period.code:
                        exist_line = pos_line_obj.search(cr, uid, [('student_id', '=', student.id), ('type', '=', 'club'), ('period_id', '=', period.id),('subscriber', '=', True)])
                        for line in pos_line_obj.browse(cr, uid, exist_line):
                            if line.product_id.product_tmpl_id.pos_categ_id.id == product_tmpl.pos_categ_id.id:
                                raise osv.except_osv(_('Warning!'), _('The %s club already exist in %s.') % (data.club_id.name, period.name))

                        product_id = product_obj.search(cr, uid, [('product_tmpl_id', '=', product_tmpl.id)], limit=1, context=context)[0]

                        inv = pos_line_obj.onchange_product_id(cr, uid, product_id, student.parent_id.property_product_pricelist.id, product_id, 1, student.parent_id.id)

                        inv['value']['product_id'] = product_id

                        inv['value']['product_id_tmpl'] = product_tmpl.id
                        inv['value']['student_id'] = student.id
                        inv['value']['parent_id'] = student.parent_id.id
                        inv['value']['type'] = product_obj.browse(cr, uid, product_id).product_tmpl_id.pos_categ_id.product_category.name
                        inv['value']['qty'] = 1.0
                        inv['value']['discount'] = data.discount
                        inv['value']['group_id'] = student.group_id.id
                        inv['value']['class_id'] = student.class_id.id
                        inv['value']['academic_year_id'] = student.academic_year_id.id
                        inv['value']['period_id'] = period.id
                        inv['value']['product_category_id'] = product_obj.browse(cr, uid, product_id).product_tmpl_id.pos_categ_id.product_category.id
                        inv['value']['discount_on_product'] = float(product_obj.browse(cr, uid, product_id).list_price - inv['value']['price_unit'])


                        pos_line_obj.create(cr, uid, inv['value'], context=context)
                        code = period.code.split("/")
                        month_days = calendar.monthrange(int(code[1]), int(code[0]))[1]
                        for inc in range(0, month_days):
                                self.pool.get('oschool.student_club_presence').create(cr, uid, {
                                    'student_id': student.id,
                                    'club_id': product_tmpl.pos_categ_id,
                                    'academic_year': student.academic_year_id.id,
                                    'period_id': period.id,
                                    'product_id': product_id,
                                    'day': '%s/%s/%s' % ( str(inc + 1),code[0], code[1]),
                                })

        return {'type': 'ir.actions.act_window_close'}

class pos_line_update(osv.osv_memory):
    _name = "oschool.club.update"
    _description = "Update Club"

    subscriber = fields.Boolean("Subscriber", default=1)
    discount = fields.Float('Discount', digits=dp.get_precision('Discount'))

    def move_line(self, cr, uid, ids, context):
        pos_line_obj = self.pool.get('pos.order.line')
        line_id = context.get('active_id')
        old_line = pos_line_obj.browse(cr, uid, line_id)
        data = self.browse(cr, uid, ids, context=context)[0]
        pos_line_obj.write(cr, uid, old_line.id, {'subscriber': data.subscriber, 'discount': data.discount})

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
