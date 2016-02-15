# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
#/#############################################################################
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import SUPERUSER_ID
import time

class oschool_extra(osv.osv):
    _inherit = 'product.template'

    _columns = {
        'ticket': fields.boolean('Restaurant Ticket'),
        'ticket_type' : fields.selection([('single', "Single"), ('pack', "Pack")], string="Ticket type"),
        'ticket_ref':fields.char(string="Ticket ref")
    }

    def create(self, cr, uid, vals, context=None):
     categ_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'product_category_extra')[1]
     if vals['categ_id'] and categ_id:
         if vals['categ_id'] == categ_id:
             property_account_income = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050005')])[0]
             vals['property_account_income'] = property_account_income
     return super(oschool_extra, self).create(cr, uid, vals, context=context)

    def _default_school_type(self, cr, uid, context=None):
        if context.get('default_is_extra'):
            res = 'extra'
        else:
            res = ''
        return res

    def _default_category(self, cr, uid, context=None):
        res = super(oschool_extra, self)._default_category(cr, uid, context)
        try:
            if context.get('default_is_extra'):
                res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'product_category_extra')[1]
        except ValueError:
            pass
        return res

    def _default_pos_category(self, cr, uid, context=None):
        res = {}
        try:
            if context.get('default_is_extra'):
                res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_extra_pos_category')[1]
        except ValueError:
            pass
        return res

    _defaults = {
        'school_product_type': _default_school_type,
        'categ_id' : _default_category,
        'pos_categ_id': _default_pos_category,
        'ticket': False,
    }

oschool_extra()

class oschool_student(osv.osv):
    _inherit = 'res.partner'

    def extra_student(self, cr, uid, ids, context=None):
        category_obj = self.pool.get('pos.category')
        pos_line_obj = self.pool.get('pos.order.line')
        period_obj = self.pool.get('account.period')
        for student in self.browse(cr, uid, ids, context=context):
            registration_id = pos_line_obj.search(cr, uid, [
                    ('student_id', '=', student.id),
                    ('type', '=', 'registration'),
                    ('academic_year_id', '=', student.academic_year_id.id),
                    ('qty', '!=', -1),
                    ('refunded', '=', False)])


            registration = pos_line_obj.browse(cr, uid, registration_id)
            if not registration.order_id or (registration.order_id and registration.order_id.state == 'draft'):
                raise osv.except_osv(_('Warning!'), _('There is no registration paid for this academic year: %s.') % student.academic_year_id.name)

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_extra_wizard')
        return {
            'name': _("Add Extra"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.extra.add',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'academic_year_id': student.academic_year_id.id,
            }
        }

    def ticket_student(self, cr, uid, ids, context=None):
        category_obj = self.pool.get('pos.category')
        pos_line_obj = self.pool.get('pos.order.line')
        period_obj = self.pool.get('account.period')
        for student in self.browse(cr, uid, ids, context=context):
            registration_id = pos_line_obj.search(cr, uid, [
                    ('student_id', '=', student.id),
                    ('type', '=', 'registration'),
                    ('academic_year_id', '=', student.academic_year_id.id),
                    ('qty', '!=', -1),
                    ('refunded', '=', False)])
            registration = pos_line_obj.browse(cr, uid, registration_id)
            if not registration.order_id or (registration.order_id and registration.order_id.state == 'draft'):
                raise osv.except_osv(_('Warning!'), _('There is no registration paid for this academic year: %s.') % student.academic_year_id.name)

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_ticket_wizard')
        return {
            'name': _("Add Ticket"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.ticket.add',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'academic_year_id': student.academic_year_id.id,
            }
        }

    _columns = {
        'extra_ids': fields.one2many('pos.order.line', 'student_id', 'Extra list', \
                            domain=[('type', '=', 'extra'), ('product_id.product_tmpl_id.ticket', '=', False), ('state_academic_year', '!=', 'closed')]),
        'ticket_ids': fields.one2many('oschool.ticket', 'student_id', 'Ticket list', domain=[('product_id.product_tmpl_id.ticket', '=', True), ('state_academic_year', '!=', 'closed')]),
        'solde_ids': fields.one2many('oschool.ticket.solde', 'student_id', 'Ticket list'),

    }

oschool_student()

class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'

    def extra_payment(self, cr, uid, ids, context=None):
        pos_ref = self.pool.get('pos.order')
        pos_line_ref = self.pool.get('pos.order.line')
        product_obj = self.pool.get('product.product')
        journal_obj = self.pool.get('account.journal')
        pos_ids = []

        for line in self.pool.get('pos.order.line').browse(cr, uid, ids, context=context):
            if line.order_id:
                inv_id = line.order_id.id
            else:
                inv = {'partner_id': line.parent_id.id, 'pricelist_id': line.parent_id.property_product_pricelist.id, 'student_id': line.student_id.id}
                inv_id = pos_ref.create(cr, uid, inv, context=context)
                self.write(cr, uid, [line.id], {'order_id': inv_id}, context=context)

        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_extra_pos_form')
        res_id = res and res[1] or False
        return {
            'name': _('Payment Extra'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'domain': [('id', '=', inv_id)],
            'view_id': [res_id],
            'res_id': inv_id,
        }

    def extra_refund(self, cr, uid, ids, context=None):
        if not ids:
            return []
        clone_list = []
        inv = self.browse(cr, uid, ids[0], context=context)
        if not inv.order_id:
            student = inv.student_id
            self.unlink(cr, uid,[inv.id])
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_student_form')

            return {
            'name': _("Oschool Student"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': student.id,
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
        }
        if inv.order_id and inv.order_id.state == 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because it not payed.'))
        if inv.refunded:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it Refunded.'))
        if inv.qty < 0:
            clone_list.append(inv.order_id.id)
        else:
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
            ('state', '!=', 'closed'),
            ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise osv.except_osv(_('Error!'), _('To return product(s), you need to open a session that will be used to register the refund.'))

            order = inv.order_id
            clone_id = self.pool.get('pos.order').copy(cr, uid, order.id, {
                'name': order.name + ' REFUND', # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
                'lines' : False
            }, context=context)
            self.copy(cr, uid, inv.id, {
                'qty': -inv.qty, # not used, name forced by create
                'subscriber': False,
                'order_id':clone_id
            }, context=context)
            self.write(cr, uid, inv.id, {'refunded': True, 'subscriber': False}, context=context)
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')

            return {
                'name': _("Refund Extra"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': clone_id,
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'pos.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'nodestroy': True,
                'context': {
                    'subscription_month': inv.period_id.code,
                }
            }

pos_order_line()

class oschool_ticket(osv.osv):
    _name = 'oschool.ticket'
    _inherits =  {'pos.order.line': 'line_id'}

    def extra_payment(self, cr, uid, ids, context=None):
        pos_line_obj= self.pool.get('pos.order.line')
        id = self.browse(cr, uid, ids).line_id.id
        return pos_line_obj.extra_payment(cr, uid, id, context)

    def ticket_refund(self, cr, uid, ids, context=None):
        if not ids:
            return []
        clone_list = []
        inv = self.browse(cr, uid, ids[0], context=context)
        #on test si il y a des ticket déjà utlisé
        ticket_obj = self.pool.get('oschool.ticket.solde')
        ticket_ids = ticket_obj.search(cr, uid, [
            ('ticket_id','=',ids[0]),
            ('ticket_date_use','!=',False),
        ])
        if ticket_ids and inv.order_id == False:
            raise osv.except_osv(_('Warning!'), _('Some of ticket are used and the pack is not paid, please select another line.'))

        if not inv.order_id:
            student = inv.student_id
            self.pool.get('pos.order.line').unlink(cr, uid,[inv.line_id.id])

            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_student_form')

            return {
            'name': _("Oschool Student"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': student.id,
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
        }


        if inv.refunded:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it Refunded.'))
        if inv.qty < 0:
            clone_list.append(inv.order_id.id)
        else:
            current_session_ids = self.pool.get('pos.session').search(cr, uid, [
            ('state', '!=', 'closed'),
            ('user_id', '=', uid)], context=context)
            if not current_session_ids:
                raise osv.except_osv(_('Error!'), _('To return product(s), you need to open a session that will be used to register the refund.'))

            order = inv.order_id
            clone_id = self.pool.get('pos.order').copy(cr, uid, order.id, {
                'name': order.name + ' REFUND', # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
                'lines' : False
            }, context=context)
            self.copy(cr, uid, inv.id, {
                'qty': -inv.qty, # not used, name forced by create
                'subscriber': False,
                'order_id':clone_id
            }, context=context)
            self.write(cr, uid, inv.id, {'refunded': True, 'subscriber': False}, context=context)
            # s'il y a des ticket relier à cette ligne on les supprimes
            ticket_ids = ticket_obj.search(cr, uid, [
                ('ticket_id','=',inv.id),
                ('ticket_date_use','=',False)
            ])
            ticket_obj.unlink(cr, uid, ticket_ids)

            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')

            return {
                'name': _("Refund Ticket"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': clone_id,
                'view_id': view_id,
                'view_type': 'form',
                'res_model': 'pos.order',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
                'context': {
                    'subscription_month': inv.period_id.code,
                }
            }

    _columns = {
        'line_id': fields.many2one('pos.order.line', 'Line', ondelete='cascade', required=True, auto_join=True),
         't_from': fields.char('From'),
        't_to': fields.char('To'),
        'ref': fields.char('REF'),
    }

oschool_ticket()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
