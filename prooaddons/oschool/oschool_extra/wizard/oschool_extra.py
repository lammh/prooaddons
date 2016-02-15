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
import openerp.addons.decimal_precision as dp
from datetime import date, datetime
from openerp import fields, models, api, exceptions


class oschool_extra_add(osv.osv_memory):
    _name = "oschool.extra.add"
    _description = "Add extra"

    product_id = fields.Many2one('product.product', 'Product', domain=[('school_product_type', '=', 'extra'), ('ticket', '=', False)], required=True, change_default=True)
    qty = fields.Float('Quantity', digits_compute=dp.get_precision('Product UoS'), required=True, default=1)
    discount = fields.Float('Discount', digits=dp.get_precision('Discount'))

    def product_id_change(self, cr, uid, ids, product_id, qty, context=None):
        context = context or {}
        if not product_id:
            return {}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        if product.virtual_available < qty:
            #raise osv.except_osv(_('Warning!'), _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
            #            (qty, max(0, product.virtual_available), max(0, product.qty_available)))
            raise osv.except_osv(_('Error!'),  _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
                        (qty, max(0, product.virtual_available), max(0, product.qty_available)))
        return {}

    def move_line(self, cr, uid, ids, context):
        pos_line_obj = self.pool.get('pos.order.line')
        academic_year_obj = self.pool.get('oschool.academic_year')
        student = self.pool.get('res.partner').browse(cr, uid, context.get('active_id'))
        data = self.browse(cr, uid, ids, context=context)[0]
        inv = pos_line_obj.onchange_product_id(cr, uid, data.id, student.parent_id.property_product_pricelist.id, data.product_id.id, 1, student.parent_id.id)

        today = date.today()
        academic_year = academic_year_obj.browse(cr, uid, context.get('academic_year_id'))
        first_period = academic_year.period_ids[0]
        period_id = False
        for period in academic_year.period_ids:
            if first_period.date_start > period.date_start:
                first_period = period
            if str(today) >= period.date_start and str(today) <= period.date_stop:
                period_id = period.id
                break
        if not period_id:
            period_id = first_period.id

        inv['value']['product_id_tmpl'] = data.product_id.id
        inv['value']['product_id'] = data.product_id.id
        inv['value']['student_id'] = student.id
        inv['value']['parent_id'] = student.parent_id.id
        inv['value']['type'] = 'extra'
        inv['value']['qty'] = data.qty
        inv['value']['discount'] = data.discount
        inv['value']['period_id'] = period_id
        inv['value']['academic_year_id'] = context.get('academic_year_id')
        inv['value']['discount_on_product'] = float(data.product_id.list_price - inv['value']['price_unit'])

        product =  data.product_id
        if product.virtual_available < data.qty:
            raise osv.except_osv(_('Error!'),  _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
                        (data.qty, max(0, product.virtual_available), max(0, product.qty_available)))
        else:
            id = pos_line_obj.create(cr, uid, inv['value'], context=context)
            pos_line_obj.write(cr, uid, id, {'period_id':period_id})
        return {'type': 'ir.actions.act_window_close'}

class oschool_ticket_add(osv.osv_memory):
    _name = "oschool.ticket.add"
    _description = "Add ticket"

    product_id = fields.Many2one('product.product', 'Product', domain=[('ticket', '=', True)], required=True, change_default=True)
    ref = fields.Char('Ref', size=64)
    prefix = fields.Char('Prefix', compute="set_prefix")
    t_from = fields.Integer('From')
    t_to = fields.Integer('To')
    ticket_type = fields.Selection([('single', "Single"), ('pack', "Pack")], string="Ticket type")

    @api.one
    @api.depends('product_id')
    def set_prefix(self):
        if self.product_id:
            comany = self.product_id.company_id.name[0]
            year = str(datetime.today().year)
            product = self.product_id.ticket_ref

            self.prefix = comany+ product + "/" + year
    def ticket_type_change(self, cr, uid, ids, ticket_type, context=None):
        if not ticket_type:
            return {}
        else:
            ids = self.pool.get('product.product').search(cr, uid, [
                ('ticket','=',True),
                ('ticket_type','=',ticket_type),
            ], context=context)
            return {'domain':{'product_id':[('id', 'in',ids )]}}

    def product_id_change(self, cr, uid, ids, product_id, context=None):
        context = context or {}
        if not product_id:
            return {}
        product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        if product.virtual_available < 1:
            #raise osv.except_osv(_('Warning!'), _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
            #            (qty, max(0, product.virtual_available), max(0, product.qty_available)))
            raise osv.except_osv(_('Error!'),  _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
                        (1, max(0, product.virtual_available), max(0, product.qty_available)))

        return {}

    def move_line(self, cr, uid, ids, context):
        ticket_obj = self.pool.get('oschool.ticket')
        student = self.pool.get('res.partner').browse(cr, uid, context.get('active_id'))
        data = self.browse(cr, uid, ids, context=context)[0]
        inv = self.pool.get('pos.order.line').onchange_product_id(cr, uid, data.id, student.parent_id.property_product_pricelist.id, data.product_id.id, 1, student.parent_id.id)
        inv['value']['product_id'] = data.product_id.id
        inv['value']['student_id'] = student.id
        inv['value']['parent_id'] = student.parent_id.id
        inv['value']['type'] = 'extra'
        inv['value']['qty'] = 1
        inv['value']['ref'] = data.ref
        inv['value']['academic_year_id'] = context.get('academic_year_id')
        inv['value']['t_from'] = data.t_from
        inv['value']['t_to'] = data.t_to
        inv['value']['discount_on_product'] = float(data.product_id.list_price - inv['value']['price_unit'])

        product =  data.product_id
        if product.virtual_available < 1:
            raise osv.except_osv(_('Error!'),  _('Not enough stock!: \n\n You plan to sell %.2f but you only have %.2f available !\nThe real stock is %.2f. (without reservations)') % \
                        (data.qty, max(0, product.virtual_available), max(0, product.qty_available)))
        else:
            ticket_id = ticket_obj.create(cr, uid, inv['value'], context=context)
        if data.ticket_type == 'single':
            if data.ref:
                solde_obj = self.pool.get('oschool.ticket.solde')
                solde_obj.create(cr, uid,
                                 {
                                    'name':data.prefix+'/'+data.ref,
                                     'student_id':student.id,
                                     'ticket_id':ticket_id
                                  }
                                 , context=context)
            else:
                raise osv.except_osv(_('Error!'),  _('Invalid REF'))
        elif data.ticket_type == 'pack':
            if data.t_from and data.t_to:
                if int(data.t_from) <= int(data.t_to):
                    solde_obj = self.pool.get('oschool.ticket.solde')
                    for i in range(int(data.t_from),int(data.t_to)+1):
                        solde_obj.create(cr, uid,
                                         {
                                            'name':data.prefix +'/'+str(i),
                                            'student_id':student.id,
                                            'ticket_id':ticket_id
                                         }
                                         , context=context)
                else:
                    raise osv.except_osv(_('Error!'),  _('Invalid range'))
            else:
                raise osv.except_osv(_('Error!'),  _('Invalid REF'))
        return {'type': 'ir.actions.act_window_close'}
class oschool_ticket_solde(models.Model):
    _name='oschool.ticket.solde'
    _order = 'ticket_date_use DESC'

    name = fields.Char('Name')
    ticket_date_use = fields.Datetime('Date of use')
    ticket_id =  fields.Many2one('oschool.ticket', string="Ticket",ondelete="cascade")
    student_id = fields.Many2one('res.partner', string="Student",ondelete="cascade")

    _sql_constraints = [
        ('unique_name', 'unique(name)', 'Ticket already exist!'),
        ('unique_ticket_date_use', 'unique(ticket_date_use,student_id)', 'Student can\'t use two ticket on the same day!')
    ]


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
