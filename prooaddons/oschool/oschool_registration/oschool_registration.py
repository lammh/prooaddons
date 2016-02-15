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
from openerp import SUPERUSER_ID
import time
from openerp.tools.translate import _
from openerp import models, api
import openerp.addons.decimal_precision as dp
from datetime import datetime
from dateutil import relativedelta

class oschool_student(osv.osv):
    _inherit = 'res.partner'

    def registration_student(self, cr, uid, ids, context=None):
        if not ids: return []
        current_session_ids = self.pool.get('pos.session').search(cr, uid, [
        ('state', '!=', 'closed'),
        ('user_id', '=', uid)], context=context)
        if not current_session_ids:
            raise osv.except_osv(_('Error!'), _('Open a session first.'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_student_registration_dialog_form')

        inv = self.browse(cr, uid, ids[0], context=context)
        return {
            'name':_("Registration Student"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'pos.order.line',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_student_id': inv.id,
                'default_type': 'registration',
                'type': 'registration'
            }
        }

    _columns = {
        'registration_ids': fields.one2many('pos.order.line', 'student_id', 'Registration List', domain=[('type' , '=', 'registration')]),
    }

oschool_student()

class pos_order_line(osv.osv):
    _inherit = 'pos.order.line'

    def registration_refund(self, cr, uid, ids, context=None):
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
            student = inv.student_id
            self.pool.get('pos.order').unlink(cr, uid, inv.order_id.id)
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

        if inv.refunded:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it Refunded.'))
        if inv.qty < 0:
            clone_list.append(inv.order_id.id)
        else:
            line_obj = self.pool.get('pos.order.line')
            student_obj = self.pool.get('res.partner')

            for order in self.browse(cr, uid, ids, context=context).order_id:
                current_session_ids = self.pool.get('pos.session').search(cr, uid, [
                ('state', '!=', 'closed'),
                ('user_id', '=', uid)], context=context)
                if not current_session_ids:
                    raise osv.except_osv(_('Error!'), _('To return product(s), you need to open a session that will be used to register the refund.'))

                clone_id = self.pool.get('pos.order').copy(cr, uid, order.id, {
                'name': order.name + ' REFUND', # not used, name forced by create
                'session_id': current_session_ids[0],
                'date_order': time.strftime('%Y-%m-%d %H:%M:%S'),
            }, context=context)
                clone_list.append(clone_id)

            for clone in self.pool.get('pos.order').browse(cr, uid, clone_list, context=context):
                for order_line in clone.lines:
                    line_obj.write(cr, uid, [order_line.id], {
                    'qty': -order_line.qty
                }, context=context)
            line_obj.write(cr, uid, inv.id, {'refunded': True}, context=context)
            student_obj.write(cr, uid, inv.student_id.id, {'academic_year_id': False,'group_id': False,'class_id': False}, context=context)
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')

        return {
            'name': _("Refund Registration"),
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': clone_list[0],
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'nodestroy': False,
            'target': 'new',
            'context': {
                'subscription_month': inv.period_id.code,
            }
        }

    def button_registration_pay(self, cr, uid, ids, context=None):
        return self.action_payment(cr, uid, ids, context=None)
    def button_registration(self, cr, uid, ids, context=None):
        return True

    def action_payment(self, cr, uid, ids, context=None):
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
                user = self.pool.get('res.users').browse(cr,uid,uid)
                seq_id = user.pos_config.sequence_id
                name = self.pool.get('ir.sequence').next_by_id(cr, uid, seq_id.id)
                #Ici on force le pos order de prendre la réference correcte
                #calculée en utilisant le user_id
                pos_ref.write(cr, uid,inv_id, {'name':name})

                journal_registration = journal_obj.search(cr, uid, [('registration', '=', True)], context=context)
                if journal_registration:
                    cr.execute('update pos_order set sale_journal = %s where id = %s', (journal_registration[0], inv_id))

                self.write(cr, uid, [line.id], {'order_id': inv_id}, context=context)

        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_registration_pos_form')
        res_id = res and res[1] or False
        return {
            'name': _('Payment Registration'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'pos.order',
            'type': 'ir.actions.act_window',
            'target' : 'new',
            'domain': [('id', '=', inv_id)],
            'view_id': [res_id],
            'res_id': inv_id,
        }

    def onchange_registration(self, cr, uid, ids, student_id, product_id, group_id):
        res = {'value': {}}
        if product_id:
            product = self.pool.get('product.product').browse(cr, uid, product_id)
            res['value']['academic_year_id'] = product.pos_categ_id.academic_year.id
        if not student_id:
            return res
        else:
            partner_obj = self.pool.get('res.partner')
            student = partner_obj.browse(cr, uid, student_id)
            partner_id = student.parent_id
            if not student.allow_registration:
                return {'value': {'student_id': False}, 'Warning': {'title': _('Warning!'), 'message': _('No allow student registration.')}}
            res = self.onchange_product_id(cr, uid, ids, pricelist=partner_id.property_product_pricelist.id, product_id=product_id, qty=1, partner_id=partner_id.id)
            if product_id:
                product = self.pool.get('product.product').browse(cr, uid, product_id)
                reg = self.search(cr, uid, [
                    ('type', '=', 'registration'),
                    ('academic_year_id', '=', product.pos_categ_id.academic_year.id),
                    ('student_id', '=', student_id),
                    ('qty', '!=', -1),
                    ('refunded', '=', False),
                ])
                if len(reg) > 0:
                    raise osv.except_osv(_('Warning!'), _('Student already registered.'))
                    return {'value': {'product_id': False}, 'Warning': {'title': _('Warning!'), 'message': _('Student already registered.')}}

                res['value']['academic_year_id'] = product.pos_categ_id.academic_year.id
                res['value']['registration_price'] = res['value']['price_unit']
        if group_id and product_id:
            group = self.pool.get('oschool.groups').browse(cr, uid, group_id)
            number_of_places = group.number_of_places
            reg = self.search(cr, uid, [('type', '=', 'registration'), ('academic_year_id', '=', product.pos_categ_id.academic_year.id), ('group_id', '=', group_id), ('qty', '!=', -1)])
            if number_of_places <= len(reg):
                raise osv.except_osv(_('Warning!'), _('Full Group.'))
                return {'value': {'group_id': False}, 'Warning': {'title': _('Warning!'), 'message': _('Full Group.')}}
            res['value']['remaining_places'] = number_of_places - len(reg)
        today = datetime.today()
        line_ids = self.pool.get('pos.order.line').search(cr, uid,[
            ('student_id','=',student_id),
            ('order_id','=',False),
            ('period_id.date_start','<=',datetime.strftime(today, "%Y-%m-%d"))
        ])
        if line_ids:
            raise osv.except_osv(_('Warning!'), _('Student have unpaid lines.'))

        return res

    def onchange_group(self, cr, uid, ids, group_id, academic_year_id, context=None):
        if not academic_year_id and group_id:
            return {'value': {'remaining_places': 0,'group_id': False}, 'warning': {'title': _('Warning!'), 'message': _('Choose Registration Type first.')}}
        if not academic_year_id or not group_id:
            return {'value': {'remaining_places': 0}}
        number_of_places = self.pool.get('oschool.groups').browse(cr, uid, group_id, context=context).number_of_places
        reg = self.search(cr, uid, [
            ('type', '=', 'registration'),
            ('academic_year_id', '=', academic_year_id),
            ('group_id', '=', group_id),
            ('qty', '>', 0),
            ('refunded','=',False)], context=context)

        if number_of_places <= len(reg):
            return {'value': {'group_id': False}, 'Warning': {'title': _('Warning!'), 'message': _('Full Group.')}}
        return {'value': {'remaining_places': number_of_places - len(reg)}}

    def create(self, cr, uid, values, context=None):
        partner_obj = self.pool.get('res.partner')
        res = super(pos_order_line, self).create(cr, uid, values, context=context)
        period_obj = self.pool.get('account.period')
        if 'type' in values:
            if values['type'] == 'registration':
                self.action_payment(cr, uid, [res], context)
                create_date = time.strftime('%Y-%m-%d')
                period_id = period_obj.search(cr, uid, [('date_start', '<=', create_date), ('date_stop', '>=', create_date), ('state', '=', 'draft')], context=context)
                if not period_id:
                    raise osv.except_osv(_('Warning!'), _('There is no period defined for this date: %s.') % create_date)
                product = self.pool.get('product.product').browse(cr, uid, values['product_id'])
                self.write(cr, uid, res, {'period_id': period_id[0], 'academic_year_id': product.pos_categ_id.academic_year.id}, context=context)
                student = partner_obj.browse(cr, uid, values['student_id'])
                state_academic_year = product.pos_categ_id.academic_year.state
                if not student.academic_year_id or state_academic_year == 'current':
                    partner_obj.write(cr, uid, student.id, {'academic_year_id': product.pos_categ_id.academic_year.id})
                if not student.group_id or state_academic_year == 'current':
                    partner_obj.write(cr, uid, student.id, {'group_id': values['group_id']})
                if not student.class_id and values['class_id'] or state_academic_year == 'current':
                    partner_obj.write(cr, uid, student.id, {'class_id': values['class_id']})
                check_minimum_age_registration = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.check_minimum_age_registration", default=None, context=context)
                company_id =self.pool.get("res.users").browse(cr, uid, uid).company_id.id
                activate_check_minimum_age_registration = self.pool.get("res.company").browse(cr, uid, company_id).activate_check_minimum_age_registration
                group =self.pool.get("oschool.groups").browse(cr, uid, values['group_id'])
                if check_minimum_age_registration:
                    if activate_check_minimum_age_registration:
                        registration_min_age_year = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.registration_min_age_year", default=None, context=context)
                        registration_min_age_month = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.registration_min_age_month", default=None, context=context)
                        dt = datetime.strptime(product.pos_categ_id.academic_year.date_start, '%Y-%m-%d')
                        dt2 = datetime.strptime(student.birthdate, '%Y-%m-%d')
                        date_difference = relativedelta.relativedelta(dt, dt2)
                        if int(date_difference.years) > int(registration_min_age_year):
                            return res
                        if int(date_difference.years) == int(registration_min_age_year) and int(date_difference.months) >= int(registration_min_age_month):
                            return res
                        else:
                            raise osv.except_osv(_('Error!'), _('the student does not have the age required for registration'))
                    else:
                        return res
        return res

    def _compute(self, cr, uid, ids, field_names, arg=None, context=None, query='', query_params=()):
        res = {}
        return res

    def _registration_price(self, cr, uid, ids, field_names, arg=None, context=None, query='', query_params=()):
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res = self.onchange_product_id(cr, uid, ids, pricelist=line.parent_id.property_product_pricelist.id, product_id=line.product_id.id, qty=1, partner_id=line.parent_id.id)
            res[line.id] = res['value']['price_unit']
        return res
    def unlink(self, cr, uid, ids, context=None):
        # boucle pour supprimer +eurs enregistrements aux meme temps
        for id in ids:
            line =  self.browse(cr, uid, id)
            # inv = self.browse(cr, uid, ids[0], context=context)
            # #****Club presence*****
            # if line.order_id.type=='club':
            #     presence_club_obj = self.pool.get('oschool.student_club_presence')
            #     presence_club_ids = presence_club_obj.search(cr, uid, [])
            #     presence_club_obj.unlink(cr, uid, presence_club_ids)
            # #****transport presence*****
            # if line.order_id.type=='transport':
            #     presence_transport_obj = self.pool.get('oschool.student_transport_presence')
            #     presence_transport_ids = presence_transport_obj.search(cr, uid, [])
            #     presence_transport_obj.unlink(cr, uid, presence_transport_ids)
            # #****restaurant presence*****
            # if line.order_id.type=='restaurant':
            #     presence_restaurant_obj = self.pool.get('oschool.student_restaurant_presence')
            #     presence_restaurant_ids = presence_restaurant_obj.search(cr, uid, [])
            #     presence_restaurant_obj.unlink(cr, uid, presence_restaurant_ids)
            # #****canteen presence*****
            # if line.order_id.type=='restaurant':
            #     presence_canteen_obj = self.pool.get('oschool.student_canteen_presence')
            #     presence_canteen_ids = presence_canteen_obj.search(cr, uid, [])
            #     presence_canteen_obj.unlink(cr, uid, presence_canteen_ids)
            if line.order_id:
                if len(line.order_id.lines) == 1:
                    order_id = line.order_id.id
                    super(pos_order_line, self).unlink(cr, uid, id, context)
                    self.pool.get('pos.order').unlink(cr, uid, order_id)
            else:
                super(pos_order_line, self).unlink(cr, uid, id, context)
        return  True
    _columns = {
        'remaining_places': fields.function(_compute, type='integer', string='Remaining places'),
        'registration_price': fields.function(_registration_price, type='float', digits_compute=dp.get_precision('Product Price'), string='Price'),
    }

pos_order_line()

class pos_order(osv.osv):
    _inherit = 'pos.order'

    def fields_view_get(self, cr, uid, view_id=None, view_type=False, context=None, toolbar=False, submenu=False):
        mod_obj = self.pool.get('ir.model.data')
        if context is None: context = {}
        if view_type == 'form':
            if context.get('pos_id') == 'pos':
                result = mod_obj.get_object_reference(cr, uid, 'oschool', 'view_oschool_registration_pos_form')
                result = result and result[1] or False
                view_id = result

        res = super(pos_order, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        return res


pos_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
