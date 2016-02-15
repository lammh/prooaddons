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

from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp

class sale_report(osv.osv):
    _name = "pos.report"
    _description = "Point of Sale Orders Statistics"
    _auto = False
    _rec_name = 'name'

    _columns = {
        'id': fields.integer('Id'),
        'company_id': fields.many2one('res.company', 'Company'),
        'name': fields.char('Line No'),
        'notice': fields.char('Discount Notice'),
        'product_id': fields.many2one('product.product', 'Product'),
        'price_unit': fields.float(string='Unit Price', digits_compute=dp.get_precision('Product Price')),
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product UoS')),
        'price_subtotal': fields.float(digits_compute=dp.get_precision('Product Price'), string='Subtotal w/o Tax',),
        'price_subtotal_incl': fields.float(digits_compute=dp.get_precision('Account'), string='Subtotal'),
        'discount': fields.float('Discount (%)', digits_compute=dp.get_precision('Account')),
        'order_id': fields.many2one('pos.order', 'Order Ref'),
        'student_id': fields.many2one('res.partner', 'Student'),
        'parent_id': fields.many2one('res.partner', string='Responsible'),
        'period_id': fields.many2one('account.period', 'Period'),
        'academic_year_id': fields.many2one('oschool.academic_year', 'Academic year'),
        'type': fields.char('Type'),
        'refunded': fields.boolean('Refunded'),
        'subscriber': fields.boolean("Subscriber"),
        'product_category_id': fields.many2one('product.category', string='Category of Product'),
        'class_id': fields.many2one('oschool.classes', 'Class'),
        'product_id_tmpl': fields.many2one('product.template', 'Product'),
        'group_id': fields.many2one('oschool.groups', 'Group'),
        'date_order': fields.datetime('Order Date'),
        'discount_on_product': fields.float('Discount')
    }
    _order = 'period_id'


    def init(self, cr):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""CREATE or REPLACE VIEW %s as (
            SELECT pol.id, pol.name, pol.order_id, pol.price_unit, pol.price_subtotal,
             pol.company_id, pol.price_subtotal_incl, pol.qty, pol.discount,pol.product_id, pol.student_id, pol.subscriber, pol.parent_id,
             pol.product_category_id, pol.refunded, pol.type, pol.academic_year_id, pol.period_id,
             pol.class_id, pol.product_id_tmpl, pol.group_id, pol.date_order, pol.discount_on_product
            FROM pos_order_line pol left outer join pos_order po on po.id = pol.order_id
            WHERE pol.order_id is null or po.state = 'draft'
            )""" % (self._table,))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
