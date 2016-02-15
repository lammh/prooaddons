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
from openerp.addons.oschool import tools
import logging
_logger = logging.getLogger(__name__)

class oschool_service_generate(osv.osv_memory):
    _name = "oschool.service.generate"
    _description = "Generate Service"

    def onchange_service(self, cr, uid, ids, service_id, context):
        if not service_id:
            return {}
        student_id = context.get('active_id')
        student = self.pool.get('res.partner').browse(cr, uid, student_id)
        if context.get('academic_year_id'):
            pos_line_obj = self.pool.get('pos.order.line')
            exist = []
            data = []
            for service in self.pool.get('pos.category').browse(cr, uid, service_id).services_ids:
                id = self.pool.get('account.period').search(cr, uid, [
                    ('code', '=', service.subscription_month),
                    ('company_id','=',tools.get_default_company(self,cr,uid)),
                    ('date_stop', '>=', student.date),
                ])
                data.append(self.pool.get('account.period').browse(cr, uid, id))
            data = sorted( list( set( data ) ),key=lambda data: data[0].date_start )

            for x in self.pool.get('pos.order.line').search(cr, uid, [('product_id.pos_categ_id', '=', service_id), ('student_id', '=', student.id), ('subscriber', '=', True)]):
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

    service_id = fields.Many2one('pos.category', 'Service', required=True, select=True, domain="[('school_product_type', '=', 'service'), ('academic_year', '=', context.get('academic_year_id'))]")
    period_ids = fields.Many2many('account.period', 'service_student_generate_rel', 'service_id', 'period_id', string='Periods', default=_default_periods, domain="[('state', '=', 'draft'), ('special', '=', False)]")
    student_id = fields.Many2one('res.partner', 'Student')
    discount_service = fields.Float('Discount', digits=dp.get_precision('Discount'))

    def generate(self, cr, uid, ids, context=None):
        category_obj = self.pool.get('pos.category')
        pos_line_obj = self.pool.get('pos.order.line')
        restaurant_category = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool','oschool_service_restaurant_product_category')[1]
        canteen_category = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool','oschool_service_panier_product_category')[1]


        data = self.browse(cr, uid, ids, context=context)[0]
        product_obj = self.pool.get('product.product')
        for student in self.pool.get('res.partner').browse(cr, uid, context.get('active_id'), context=context):
            for period in data.period_ids:
                for product_tmpl in data.service_id.services_ids:
                    if product_tmpl.subscription_month == period.code:

                        exist_line = pos_line_obj.search(cr, uid, [('student_id', '=', student.id), ('type', '=', 'service'), ('period_id', '=', period.id),('subscriber', '=', True)])
                        for line in pos_line_obj.browse(cr, uid, exist_line):
                            if line.product_id.product_tmpl_id.pos_categ_id.id == product_tmpl.pos_categ_id.id:
                                raise osv.except_osv(_('Warning!'), _('The %s service already exist in %s.') % (data.service_id.name, period.name))
                            if line.product_id.product_tmpl_id.pos_categ_id.excluded_services_ids and product_tmpl.pos_categ_id in line.product_id.product_tmpl_id.pos_categ_id.excluded_services_ids:
                                raise osv.except_osv(_('Warning!'), _('The %s and %s services can not be set in %s.') % (product_tmpl.pos_categ_id.name, line.product_id.product_tmpl_id.pos_categ_id.name, period.name))
                            if product_tmpl.pos_categ_id.excluded_services_ids and line.product_id.product_tmpl_id.pos_categ_id in product_tmpl.pos_categ_id.excluded_services_ids:
                                raise osv.except_osv(_('Warning!'), _('The %s and %s services can not be set in %s.') % (product_tmpl.pos_categ_id.name, line.product_id.product_tmpl_id.pos_categ_id.name, period.name))

                        product_id = product_obj.search(cr, uid, [('product_tmpl_id', '=', product_tmpl.id)], limit=1, context=context)[0]

                        inv = pos_line_obj.onchange_product_id(cr, uid, product_id, student.parent_id.property_product_pricelist.id, product_id, 1, student.parent_id.id)

                        inv['value']['academic_year_id'] = student.academic_year_id.id

                        inv['value']['product_id'] = product_id

                        inv['value']['product_id_tmpl'] = product_tmpl.id
                        # inv['value']['product_id'] = product_tmpl.product_variant_ids[0].id
                        inv['value']['group_id'] = student.group_id.id
                        inv['value']['class_id'] = student.class_id.id
                        inv['value']['student_id'] = student.id
                        inv['value']['parent_id'] = student.parent_id.id
                        #inv['value']['type'] = 'service'
                        inv['value']['type'] = product_tmpl.pos_categ_id.product_category.name
                        inv['value']['qty'] = 1.0
                        inv['value']['discount'] = data.discount_service
                        inv['value']['period_id'] = period.id
                        inv['value']['product_category_id'] = product_obj.browse(cr, uid, product_id).product_tmpl_id.pos_categ_id.product_category.id
                        inv['value']['discount_on_product'] = float(product_obj.browse(cr, uid, product_id).list_price - inv['value']['price_unit'])

                        pos_line_obj.create(cr, uid, inv['value'], context=context)



                        code = period.code.split("/")
                        month_days = calendar.monthrange(int(code[1]), int(code[0]))[1]

                        if(product_tmpl.categ_id[0].id == restaurant_category):
                            for inc in range(0, month_days):
                                self.pool.get('oschool.student_restaurant_presence').create(cr, uid, {
                                    'student_id': student.id,
                                    'class_id': student.class_id.id,
                                    'academic_year': student.academic_year_id.id,
                                    'period_id': period.id,
                                    'product_id': product_id,
                                    'day': '%s/%s/%s' % ( str(inc + 1),code[0], code[1]),
                                })
                        if(product_tmpl.categ_id[0].id == canteen_category):
                            for inc in range(0, month_days):
                                self.pool.get('oschool.student_canteen_presence').create(cr, uid, {
                                    'student_id': student.id,
                                    'class_id': student.class_id.id,
                                    'academic_year': student.academic_year_id.id,
                                    'period_id': period.id,
                                    'product_id': product_id,
                                    'day': '%s/%s/%s' % ( str(inc + 1),code[0], code[1]),
                                })

        return {'type': 'ir.actions.act_window_close'}



class pos_line_update(osv.osv_memory):
    _name = "oschool.service.update"
    _description = "Update Service"

    subscriber = fields.Boolean("Subscriber")
    discount = fields.Float("Discount", digits=dp.get_precision('Discount'))

    def move_line(self, cr, uid, ids, context):
        pos_line_obj = self.pool.get('pos.order.line')
        line_id = context.get('active_id')
        old_line = pos_line_obj.browse(cr, uid, line_id)
        data = self.browse(cr, uid, ids, context=context)[0]
        pos_line_obj.write(cr, uid, old_line.id, {'subscriber': data.subscriber, 'discount': data.discount})

        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
