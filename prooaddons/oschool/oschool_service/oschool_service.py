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
from openerp import models, fields, api, exceptions, _
from openerp.osv import osv
import time
from datetime import timedelta, datetime
from operator import itemgetter
from openerp.exceptions import ValidationError
from openerp.addons.oschool import tools

class student_route(models.Model):
    _inherit = 'res.partner'

    service_ids = fields.One2many('pos.order.line', 'student_id', domain=[('type', 'in', ['Garderie','Panier','Restaurant']), ('state_academic_year', '!=', 'closed')], string='Services')

    def service_student(self, cr, uid, ids, context=None):
        if not ids:
            return []
        pos_line_obj = self.pool.get('pos.order.line')
        inv = self.browse(cr, uid, ids[0], context=context)
        registration_id = pos_line_obj.search(cr, uid, [
            ('student_id', '=', inv.id),
            ('type', '=', 'registration'),
            ('academic_year_id', '=', inv.academic_year_id.id),
            ('qty', '!=', -1),
            ('refunded', '=', False)
        ])
        registration = pos_line_obj.browse(cr, uid, registration_id)
        if not registration.order_id or (registration.order_id and registration.order_id.state == 'draft'):
            raise osv.except_osv(_('Warning!'), _('There is no registration paid for this academic year: %s.') % inv.academic_year_id.name)

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_service_generate')
        return {
            'name': _("Generate Service"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.service.generate',
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

    def update_service(self, cr, uid, ids, context=None):
        if not ids:
            return []
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.order_id:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it have a order.'))
        if inv.period_id.state != 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because period is closed.'))

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_service_wizard')
        return {
            'name': _("Update Service"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'oschool.service.update',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_subscriber': inv.subscriber,
                'default_discount': inv.discount,
            }
        }

    def service_refund(self, cr, uid, ids, context=None):
        if not ids:
            return []
        clone_list = []
        inv = self.browse(cr, uid, ids[0], context=context)

        line = self.browse(cr, uid, ids, context=context)
        rest = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_service_restaurant_product_category')
        cant = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_service_panier_product_category')

        if line.product_id.categ_id.id == rest[1]:
            presence_obj = self.pool.get('oschool.student_restaurant_presence')
            presence_ids = presence_obj.search(cr, uid, [
                ('student_id','=',line.student_id.id),
                ('period_id','=',line.period_id.id),
                ])
            presence_obj.unlink(cr, uid, presence_ids)
        elif line.product_id.categ_id.id == cant[1]:
            presence_obj = self.pool.get('oschool.student_canteen_presence')
            presence_ids = presence_obj.search(cr, uid, [
                ('student_id','=',line.student_id.id),
                ('period_id','=',line.period_id.id),
                ])
            presence_obj.unlink(cr, uid, presence_ids)

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
                'name': _("Refund Service"),
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

class oschool_student_restaurant_presence(models.Model):
    _name = 'oschool.student_restaurant_presence'

    student_id = fields.Many2one('res.partner', string='Name', required=True)
    day = fields.Date(string="Day", required=True)
    class_id = fields.Many2one('oschool.classes', 'Class')
    group_id = fields.Many2one('oschool.groups', 'Group', compute="_get_group")
    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    period_id = fields.Many2one('account.period', 'Period', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    day_num = fields.Char(string="Day", compute="_get_day", store=True)
    status = fields.Selection([('present', "Present"), ('absent', "Absent")], string="Presence")
    company_id = fields.Many2one('res.company', 'Company')

    report_id = fields.Many2one('oschool.restaurant.wizard', 'Period', readonly=True)
    active = fields.Boolean()
    _defaults = {'active': True,}

    @api.one
    @api.depends('day')
    def _get_day(self):
        day_num = self.day.split("-")
        self.day_num = str(int(day_num[2]))

    @api.one
    @api.depends('student_id')
    def _get_group(self):
        self.group_id = self.student_id.group_id.id

    # Return classes List
    def list_classes(self, cr, uid, context=None):
        ids = self.pool.get('oschool.classes').search(cr, uid, [])
        return self.pool.get('oschool.classes').name_get(cr, uid, ids, context=context)

    # Return period List
    def list_periods(self, cr, uid, context=None):
        id = self.pool.get('oschool.academic_year').search(cr, uid, [("state", "=", "current")])
        ids = []
        if id:
            for p in self.pool.get('oschool.academic_year').browse(cr, uid, id).period_ids:
                ids.append(p.id)
            periods = self.pool.get('account.period').name_get(cr, uid, ids, context=context)
            return periods
        else:
            raise exceptions.ValidationError("There is no current academic year!")


    # Return List of days
    def list_days(self, cr, uid, context=None):
        days = []
        for i in range(1, 32):
            days.append((i, str(i)))

        return days

    def print_report(self, cr, uid,current_period,current_class, context=None):
        report_restaurant_obj = self.pool.get('oschool.restaurant.wizard')
        report_ids = report_restaurant_obj.search(cr, uid, [
            ('class_id', '=', current_class),
            ('period_id', '=', current_period),
        ])
        if not report_ids:
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_restaurant_obj.create(cr, uid, vals)]
        else:
            report_restaurant_obj.unlink(cr, uid,report_ids)
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_restaurant_obj.create(cr, uid, vals)]

        if not report_ids:
            return  {}

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.report_restaurant',
            'datas': {
                    'model':'oschool.restaurant.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-pdf'
                },
            'nodestroy': True
            }


class oschool_student_canteen_presence(models.Model):
    _name = 'oschool.student_canteen_presence'

    student_id = fields.Many2one('res.partner', string='Name', required=True)
    day = fields.Date(string="Day", required=True)
    class_id = fields.Many2one('oschool.classes', 'Class')
    group_id = fields.Many2one('oschool.groups', 'Group', compute="_get_group")
    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    period_id = fields.Many2one('account.period', 'Period', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    day_num = fields.Char(string="Day", compute="_get_day", store=True)
    status = fields.Selection([('present', "Present"), ('absent', "Absent")], string="Presence")
    canteen_tickets = fields.Many2one('oschool.ticket.solde', string='Ticket', domain="[('student_id', '=',False)]", ondelete="set null")
    oschool_tiket_id = fields.Integer()
    company_id = fields.Many2one('res.company', 'Company')
    report_id = fields.Many2one('oschool.canteen.wizard', 'Period', readonly=True)
    active = fields.Boolean()
    _defaults = {'active': True,canteen_tickets:False}

    def state_change(self,cr,uid,ids, status,student_id, context=None):
        if status:
            if status == 'absent':
                return {'domain':{'canteen_tickets':[('student_id', '=',False )]}}
            elif status == 'present':
                return {'domain':{'canteen_tickets':[('student_id', '=',student_id ),('ticket_date_use', '=',False )]}}

    @api.one
    @api.depends('day')
    def _get_day(self):
        day_num = self.day.split("-")
        self.day_num = str(int(day_num[2]))

    @api.one
    @api.depends('student_id')
    def _get_group(self):
        self.group_id = self.student_id.group_id.id

    def print_report(self, cr, uid,current_period,current_class, context=None):
        report_canteen_obj = self.pool.get('oschool.canteen.wizard')
        report_ids = report_canteen_obj.search(cr, uid, [
            ('class_id', '=', current_class),
            ('period_id', '=', current_period),
        ])
        if not report_ids:
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_canteen_obj.create(cr, uid, vals)]
        else:
            report_canteen_obj.unlink(cr, uid,report_ids)
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_canteen_obj.create(cr, uid, vals)]

        if not report_ids:
            return  {}

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.report_canteen',
            'datas': {
                    'model':'oschool.canteen.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-pdf'
                },
            'nodestroy': True
            }
    def write(self, cr, uid,ids, vals, context=None):
        if 'canteen_tickets' in vals:
            if 'status' in vals:
                if not vals['status']:
                    msg = "ticket status can't be empty!"
                    raise exceptions.ValidationError(msg)
                if vals['status'] == 'present':
                    ticket_obj = self.pool.get('oschool.ticket.solde')
                    for id in ids:
                        presence = self.browse(cr, uid, id)
                        if presence.canteen_tickets:
                            ticket_obj.write(cr, uid,presence.canteen_tickets.id, {'ticket_date_use':False}, context=context)
                        ticket_obj.write(cr, uid,vals['canteen_tickets'], {'ticket_date_use':presence.day}, context=context)
            else:
                msg = "ticket status can't be empty!"
                raise exceptions.ValidationError(msg)
            if not vals['canteen_tickets']:
                for id in ids:
                    presence = self.browse(cr, uid, id)
                    if presence.canteen_tickets:
                        ticket_obj.write(cr, uid,presence.canteen_tickets.id, {'ticket_date_use':False}, context=context)
        return super(oschool_student_canteen_presence, self).write(cr, uid,ids, vals)




class oschool_ticket_presence(models.Model):
    _name = "oschool.ticket_presence"


    academic_year = fields.Many2one('oschool.academic_year',string="Academic year", required=True)
    student_id = fields.Many2one('res.partner', required=True, string="Student")
    day = fields.Selection([('1', "1"),('2', "2"),('3', "3"),('4', "4"),('5', "5"),('6', "6"),('7', "7"),('8', "8"),('9', "9"),('10', "10"),
                            ('11', "11"),('12', "12"),('13', "13"),('14', "14"),('15', "15"),('16', "16"),('17', "17"),('18', "18"),('19', "19"),('20', "20"),
                            ('21', "21"),('22', "22"),('23', "23"),('24', "24"),('25', "25"),('26', "26"),('27', "27"),('28', "28"),('29', "29"),('30', "30"),
                            ('31', "31")], required=True, string="Day")

    class_id = fields.Many2one('oschool.classes', 'Class', required=True)
    group_id = fields.Many2one('oschool.groups', 'Group', compute="_get_group")
    period_id = fields.Many2one('account.period', 'Period', required=True)
    # period_name = fields.Char(related="period_id.name")

    canteen_tickets = fields.Many2one('oschool.ticket.solde', string='Ticket',required=True, domain="[('student_id', '=',False)]", ondelete="set null")

    oschool_tiket_id = fields.Integer()
    day_num = fields.Char(string="Day", compute="_get_day", store=True)

    _defaults = {
        'company_id': tools.get_default_company,
    }

    @api.one
    @api.depends('student_id')
    def _get_group(self):
        self.group_id = self.student_id.group_id.id

    def student_change(self,cr,uid,ids, student_id, context=None):
        if student_id:
            return {'domain':{'canteen_tickets':[('student_id', '=',student_id ),('ticket_date_use', '=',False )]}}
    def academic_year_change(self,cr,uid,ids, academic_year, context=None):
        if academic_year:
            period_ids = self.pool.get('oschool.academic_year').browse(cr, uid, academic_year).period_ids
            ids = []
            for period in period_ids:
                ids.append(period.id)
            return {'domain':{'period_id':[('id', 'in',ids )]}}


    @api.one
    @api.depends('day')
    def _get_day(self):
        self.day_num = self.day

    def print_report(self, cr, uid,current_period,current_class, context=None):
        report_ticket_obj = self.pool.get('oschool.ticket.wizard')
        report_ids = report_ticket_obj.search(cr, uid, [
            ('class_id', '=', current_class),
            ('period_id', '=', current_period),
        ])
        if not report_ids:
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_ticket_obj.create(cr, uid, vals)]
        else:
            report_ticket_obj.unlink(cr, uid,report_ids)
            vals= {}
            vals['class_id'] = current_class
            vals['period_id'] = current_period
            report_ids = [report_ticket_obj.create(cr, uid, vals)]

        if not report_ids:
            return  {}

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.report_ticket',
            'datas': {
                    'model':'oschool.ticket.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-pdf'
                },
            'nodestroy': True
            }


    @api.model
    def create(self, values):
        if 'canteen_tickets' not in values:
            raise exceptions.ValidationError("There is no ticket selected!")
        else:
            obj = super(oschool_ticket_presence, self).create(values)
            day = datetime.strptime(obj.period_id.date_start, '%Y-%m-%d') + timedelta(days=int(obj.day)-1)
            obj.canteen_tickets.write( {'ticket_date_use':day})
        return obj

    def write(self, cr, uid, ids, vals, context=None):
        presence = self.browse(cr, uid, ids)
        ticket_obj = self.pool.get('oschool.ticket.solde')
        if 'canteen_tickets' in vals:
            ticket_obj.write(cr, uid, presence.canteen_tickets.id,{'ticket_date_use':False} )
            super(oschool_ticket_presence, self).write(cr, uid, ids,vals)
            presence = self.browse(cr, uid, ids)
            day = datetime.strptime(presence.period_id.date_start, '%Y-%m-%d') + timedelta(days=int(presence.day)-1)
            ticket_obj.write(cr, uid, presence.canteen_tickets.id,{'ticket_date_use':day})
        else:
            super(oschool_ticket_presence, self).write(cr, uid, ids,vals)
            presence = self.browse(cr, uid, ids)
            day = datetime.strptime(presence.period_id.date_start, '%Y-%m-%d') + timedelta(days=int(presence.day)-1)
            ticket_obj.write(cr, uid, presence.canteen_tickets.id,{'ticket_date_use':day})
        return ids
    def unlink(self, cr, uid, ids, context=None):
        presences = self.browse(cr, uid, ids)
        ticket_obj = self.pool.get('oschool.ticket.solde')
        for p in presences:
            ticket_obj.write(cr, uid, p.canteen_tickets.id,{'ticket_date_use':False} )
        return super(oschool_ticket_presence, self).unlink(cr, uid, ids)



    def default_get(self, cr, uid, fields, context=None):
        data = super(oschool_ticket_presence, self).default_get(cr, uid, fields, context=context)
        academic_year = self.pool.get('oschool.academic_year').search(cr, uid, [("state", "=", "current")])
        if academic_year:
            data['academic_year']= academic_year[0]
            return data
        else:
            raise exceptions.ValidationError("There is no current academic year!")

