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
from openerp import models, api, fields,exceptions, _
from openerp.osv import osv
import time

class student_route(models.Model):
    _inherit = 'res.partner'

    club_ids = fields.One2many('pos.order.line', 'student_id', domain=[('type', '=', 'Club'), ('state_academic_year', '!=', 'closed')], string='Clubs')

    def club_student(self, cr, uid, ids, context=None):
        if not ids:
            return []
        pos_line_obj = self.pool.get('pos.order.line')
        inv = self.browse(cr, uid, ids[0], context=context)
        registration_id = pos_line_obj.search(cr, uid, [
                    ('student_id', '=', inv.id),
                    ('type', '=', 'registration'),
                    ('academic_year_id', '=', inv.academic_year_id.id),
                    ('qty', '!=', -1),
                    ('refunded', '=', False)])

        registration = pos_line_obj.browse(cr, uid, registration_id)
        if not registration.order_id or (registration.order_id and registration.order_id.state == 'draft'):
            raise osv.except_osv(_('Warning!'), _('There is no registration paid for this academic year: %s.') % inv.academic_year_id.name)
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_club_generate')
        return {
            'name': _("Generate Club"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.club.generate',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'academic_year_id': inv.academic_year_id.id,
            }
        }

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    def update_club(self, cr, uid, ids, context=None):
        if not ids:
            return []
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.order_id:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it have a order.'))
        if inv.period_id.state != 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because period is closed.'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_club_wizard')
        return {
            'name': _("Update Club"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.club.update',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_subscriber': inv.subscriber,
            }
        }

    def club_refund(self, cr, uid, ids, context=None):
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
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_refund_pos_form')

            return {
                'name': _("Refund Registration"),
                'view_type': 'form',
                'view_mode': 'form',
                'res_id': clone_id,
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

class oschool_student_club_presence(models.Model):
    _name = 'oschool.student_club_presence'

    student_id = fields.Many2one('res.partner', string='Name', required=True)
    day = fields.Date(string="Day", required=True)
    club_id = fields.Integer()
    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    class_id = fields.Many2one('oschool.classes', 'Class', compute="_get_group_class")
    group_id = fields.Many2one('oschool.groups', 'Group', compute="_get_group_class")
    period_id = fields.Many2one('account.period', 'Period', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    day_num = fields.Char(string="Day", compute="_get_day", store=True)
    status = fields.Selection([('present', "Present"), ('absent', "Absent")], string="Presence")


    @api.one
    @api.depends('day')
    def _get_day(self):
        day_num = self.day.split("-")
        self.day_num = str(int(day_num[2]))
        # filter_lists().get_day()

    @api.one
    @api.depends('student_id')
    def _get_group_class(self):
        self.group_id = self.student_id.group_id.id
        self.class_id = self.student_id.class_id.id

    # Return classes List
    def get_list_clubs(self, cr, uid, context=None):
        club_pos_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_club_pos_category')[1]
        current_academic_year_id = self.pool.get('oschool.academic_year').search(cr, uid, [('state','=','current')])
        ids = []
        if current_academic_year_id:
            ids = self.pool.get('pos.category').search(cr, uid, [('parent_id','=',club_pos_id),('academic_year','=', current_academic_year_id[0])])
        return self.pool.get('pos.category').name_get(cr, uid, ids, context=context)

    # Return period List
    def get_list_periods(self, cr, uid, context=None):
        id = self.pool.get('oschool.academic_year').search(cr, uid, [("state", "=", "current")])
        ids = []
        if id:
            for p in self.pool.get('oschool.academic_year').browse(cr, uid, id).period_ids:
                ids.append(p.id)
            periods = self.pool.get('account.period').name_get(cr, uid, ids, context=context)
            return periods
        else:
            raise exceptions.ValidationError("There is no current academic year!")

        # return filter_lists().get_list_periods(cr,uid)
    # Return List of days
    def get_list_days(self, cr, uid, context=None):
        days = []
        for i in range(1, 32):
            days.append((i, str(i)))

        return days
        # return filter_lists().get_list_days(cr,uid)


# class filter_lists(object):
#
#     @api.one
#     @api.depends('day')
#     def get_day(self):
#         day_num = self.day.split("-")
#         self.day_num = str(int(day_num[2]))
#
#     # Return classes List
#     def get_list_clubs(self, cr, uid, context=None):
#         club_pos_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_club_pos_category')[1]
#         current_academic_year_id = self.pool.get('oschool.academic_year').search(cr, uid, [('state','=','current')])[0]
#         ids = self.pool.get('pos.category').search(cr, uid, [('parent_id','=',club_pos_id),('academic_year','=', current_academic_year_id)])
#         return self.pool.get('pos.category').name_get(cr, uid, ids, context=context)
#
#     # Return period List
#     def get_list_periods(self, cr, uid, context=None):
#         id = self.pool.get('oschool.academic_year').search(cr, uid, [("state", "=", "current")])
#         ids = []
#         if id:
#             for p in self.pool.get('oschool.academic_year').browse(cr, uid, id).period_ids:
#                 ids.append(p.id)
#             periods = self.pool.get('account.period').name_get(cr, uid, ids, context=context)
#             return periods
#         else:
#             raise exceptions.ValidationError("There is no current academic year!")
#
#
#     # Return List of days
#     def get_list_days(self, cr, uid, context=None):
#         days = []
#         for i in range(1, 32):
#             days.append((i, str(i)))
#
#         return days
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
