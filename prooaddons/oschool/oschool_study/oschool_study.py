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
from openerp import models, api
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import time

class oschool_student(osv.osv):
    _inherit = 'res.partner'

    def study_student(self, cr, uid, ids, context=None):
        category_obj = self.pool.get('pos.category')
        pos_line_obj = self.pool.get('pos.order.line')
        period_obj = self.pool.get('account.period')
        product_obj = self.pool.get('product.product')
        for student in self.browse(cr, uid, ids, context=context):
            study_id = category_obj.search(cr, uid, [
                ('school_product_type', '=', 'study'),
                ('academic_year', '=', student.academic_year_id.id),
                ('groups', '=', student.group_id.id)])
            if not study_id:
                raise osv.except_osv(_('Warning!'), _('There is no study defined for this academic year: %s.') % student.academic_year_id.name)
            registration_id = pos_line_obj.search(cr, uid, [
                ('student_id', '=', student.id),
                ('type', '=', 'registration'),
                ('academic_year_id', '=', student.academic_year_id.id),
                ('qty', '!=', -1),
                ('refunded', '=', False)])
            registration = pos_line_obj.browse(cr, uid, registration_id)
            if not registration.order_id or (registration.order_id and registration.order_id.state == 'draft'):
                raise osv.except_osv(_('Warning!'), _('There is no registration paid by %s for this academic year: %s.') % (student.display_name, student.academic_year_id.name))

            for study in category_obj.browse(cr, uid, study_id, context=context).services_ids:
                if period_obj.browse(cr, uid, period_obj.search(cr, uid, [('code', '=', study.subscription_month)])[0]).state == 'done':
                    continue
                if not period_obj.search(cr, uid, [('code', '=', study.subscription_month)]):
                    raise osv.except_osv(_('Warning!'), _('period %s not exist.') % study.subscription_month)

                product_id = product_obj.search(cr, uid, [('product_tmpl_id', '=', study.id)], limit=1, context=context)[0]

                inv = pos_line_obj.onchange_product_id(cr, uid, product_id, student.parent_id.property_product_pricelist.id, product_id, 1, student.parent_id.id)

                #inv['value']['product_id'] = study.product_variant_ids[0].id
                period_id = period_obj.search(cr, uid, [
                    ('code', '=', study.subscription_month),
                    ('company_id', '=', student.company_id.id)
                ])[0]
                period = period_obj.browse(cr, uid, period_id)
                if period.date_stop > student.date:
                    if len(pos_line_obj.search(cr, uid, [('student_id', '=', student.id),
                                                         ('type', '=', 'study'),
                                                         ('academic_year_id', '=',student.academic_year_id.id),
                                                         ('period_id', '=', period.id),
                                                         ('refunded', '=', False),
                                                        ('qty', '!=', -1)
                                                         ])) > 0:
                        continue
                    else:
                        inv['value']['product_id'] = product_id
                        inv['value']['product_id_tmpl'] = study.id
                        inv['value']['student_id'] = student.id
                        inv['value']['group_id'] = student.group_id.id
                        inv['value']['class_id'] = student.class_id.id
                        inv['value']['parent_id'] = student.parent_id.id
                        inv['value']['type'] = product_obj.browse(cr, uid, product_id).product_tmpl_id.pos_categ_id.product_category.name
                        inv['value']['qty'] = 1.0
                        inv['value']['discount'] = student.discount_study
                        inv['value']['academic_year_id'] = student.academic_year_id.id
                        inv['value']['period_id'] = period_id
                        inv['value']['product_category_id'] = product_obj.browse(cr, uid, product_id).product_tmpl_id.pos_categ_id.product_category.id
                        inv['value']['discount_on_product'] = float(product_obj.browse(cr, uid, product_id).list_price - inv['value']['price_unit'])

                        pos_line_obj.create(cr, uid, inv['value'], context=context)
        return True

    _columns = {
        'study_ids': fields.one2many('pos.order.line', 'student_id', 'Study List', domain=[('type', '=', 'Study'), ('state_academic_year', '!=', 'closed')]),
        'discount_study': fields.float('Discount', digits_compute=dp.get_precision('Discount')),
    }

oschool_student()

class pos_order_line(osv.osv):
    _inherit = "pos.order.line"

    def study_student(self, cr, uid, ids, context=None):
        if not ids:
            return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_study_wizard')
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.order_id:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it have a order.'))
        if inv.period_id.state != 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because period is closed.'))
        return {
            'name': _("Update Study"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.study.update',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_subscriber': inv.subscriber,
            }
        }

    def study_refund(self, cr, uid, ids, context=None):
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
        if not inv.subscriber:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it not subscriber.'))
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
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_study_pos_form')

            return {
                'name': _("Refund Study"),
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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
