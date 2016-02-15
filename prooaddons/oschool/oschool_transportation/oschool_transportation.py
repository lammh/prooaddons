# -*- coding: utf-8 -*-
from openerp.osv import osv
from datetime import timedelta, datetime
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import time
from openerp.addons.oschool import tools

import logging
_logger = logging.getLogger(__name__)

class oschool_zone(models.Model):
    _name = 'oschool.zone'

    name = fields.Char(string="Titre", required=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', 'Company')


    _defaults = {
        'company_id': tools.get_default_company,
    }

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name,company_id)',
         "The zone must be unique"),
    ]

class oschool_bus(models.Model):
    _name = 'oschool.bus'

    name = fields.Char(string="Serial", required=True)
    type = fields.Char(string="Type")

    seats = fields.Integer(string="Number of seats", required=True)
    description = fields.Text()
    company_id = fields.Many2one('res.company', 'Company')

    _defaults = {
        'company_id': tools.get_default_company,
    }

    @api.constrains('seats')
    def _check_seats_number(self):
        if self.seats <= 0:
             raise ValidationError("Number of the seats must be greater than 0")

    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name,company_id)',
         "The serial must be unique"),
    ]

class oschool_shuttle(models.Model):

    _name="oschool.shuttle"

    name = fields.Char(string="Shuttle", required=True)
    number_shuttle = fields.Integer("Shuttle")

class oschool_bus_schedule(models.Model):

    _name="oschool.bus_schedule"

    name = fields.Char(string="Bus schedule", required=True)

class oschool_driver_hostess_assignment(models.Model):

    _name = "oschool.driver_hostess_assignment"
    _rec_name = 'bus_to_zone_id'

    # bus_to_zone_id = fields.Integer()
    bus_to_zone_id = fields.Many2one('oschool.assign_bus_to_zone', ondelete='cascade', required=True)
    driver = fields.Many2one('hr.employee', string="Driver", required=True)
    hostess = fields.Many2one('hr.employee', string="Hostess", required=True)
    day = fields.Date(string="Day", required=True)
    bus_schedule = fields.Many2one('oschool.bus_schedule', string="Schedule", required=True)
    company_id = fields.Many2one('res.company', 'Company')


    _defaults = {
        'company_id': tools.get_default_company,
    }

    _sql_constraints = [
        ('unique_driver_assignment', 'unique(driver, day, bus_schedule)',
         "The driver can not have multiple assignments at the same time"),
        ('unique_hostess_assignment', 'unique(hostess, day, bus_schedule)',
         'The hostess can not have multiple assignments at the same time'),
        ('unique_bus_assignment', 'unique(day, bus_schedule,bus_to_zone_id)',
         'The bus can not be assigned more than once for the same period'),
    ]


class oschool_assign_bus_to_zone(models.Model):

    _name = "oschool.assign_bus_to_zone"

    name = fields.Char(required=True)
    zone = fields.Many2one('oschool.zone', ondelete='cascade', string="Zone", required=True)
    bus = fields.Many2one('oschool.bus', ondelete='cascade', string="Bus", required=True)
    start_date = fields.Date(string='Start Date', required=True)
    stop_date = fields.Date(string='End Date', required=True)
    bus_schedule_driver = fields.One2many('oschool.driver_hostess_assignment', 'bus_to_zone_id', required=True)
    driver = fields.Many2one('hr.employee', string="Driver", required=True)
    hostess = fields.Many2one('hr.employee', string="Hostess", required=True)
    company_id = fields.Many2one('res.company', 'Company')


    _defaults = {
        'company_id': tools.get_default_company,
    }

    @api.one
    @api.onchange('zone', 'bus')
    def _create_name(self):
        self.name = "%s %s %s" % (self.bus.name, "-", self.zone.name)

    def generate_bus_assignment(self, cr, uid, ids, context=None, interval=1):
        bus_schedule_driver = self.pool.get('oschool.driver_hostess_assignment')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.start_date, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.stop_date:
                de = ds + relativedelta(days=interval)
                if de.strftime('%Y-%m-%d') > fy.stop_date:
                    de = datetime.strptime(fy.stop_date, '%Y-%m-%d')
                for rec in self.pool.get('oschool.bus_schedule').search(cr, uid, []):
                    bus_schedule_driver.create(cr, uid, {
                        'bus_to_zone_id': fy.id,
                        'driver': fy.driver.id,
                        'hostess': fy.hostess.id,
                        'day': ds.strftime('%Y-%m-%d'),
                        'bus_schedule': rec,
                    })
                ds = ds + relativedelta(days=interval)
        return True



class oschool_route(models.Model):
    _inherit = 'pos.category'

    zone = fields.Many2one('oschool.zone', ondelete='cascade', string="Zone", required=False)
    shuttle = fields.Many2one('oschool.shuttle', ondelete='cascade', string="Shuttle", required=False)

    @api.one
    @api.onchange('zone', 'shuttle')
    def _create_name(self):
        self.name = "%s %s %s" % (self.zone.name, "-", self.shuttle.name)


    def generate_months_routes(self, cr, uid, ids, context=None, interval=1):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        property_account_income = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050003'),('company_id','=',company_id)])
        if not property_account_income:
            raise ValidationError("There is not account with code 7050003")
        product_template = self.pool.get('product.template')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                product_template.create(cr, uid, {
                    'name':  "%s %s %s %s" % (fy.zone.name, '-', fy.shuttle.name, ds.strftime('%m/%Y')),
                    'pos_categ_id': fy.id,
                    'type': 'service',
                    'available_in_pos': True,
                    'list_price': fy.price,
                    'property_account_income': property_account_income[0],
                    'subscription_month': ds.strftime('%m/%Y'),
                    'school_product_type': fy.school_product_type,
                    'academic_year': fy.academic_year.id,
                    'cash': fy.cash,
                    'categ_id': fy.product_category.id,

                })
                ds = ds + relativedelta(months=interval)
    _sql_constraints = [
        ('unique_route', 'unique(zone, shuttle)',
         "Route already exists!")
    ]

class oschool_student_transport_presence(models.Model):

    _name = 'oschool.student_transport_presence'

    student_id = fields.Many2one('res.partner', string='Name', required=True)
    phone = fields.Char(string="Phone")
    day = fields.Date(string="Day", required=True)
    type = fields.Char(string='Type', size=64)
    shuttle = fields.Many2one('oschool.shuttle', string="Shuttle")
    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    group_id = fields.Many2one('oschool.groups', 'Group')
    bus_schedule = fields.Many2many('oschool.bus_schedule', 'schedule_transport_presence_student_rel', 'partner_id', 'schedule_id', string='Presence')
    route_id = fields.Many2one('pos.category', string="Route")
    start_date = fields.Date(string="Start Date", compute="_set_fields", store=False)
    end_date = fields.Date(string="End Date", compute="_set_fields", store=False)

    zone_id = fields.Many2one('oschool.zone', string="Zone", compute="_get_zone", store=True)
    phone = fields.Char(compute="_get_phone", string="Phone")
    type_navette = fields.Char(compute="_get_type_navette", string="Shuttle")
    code_navette = fields.Char(compute="_get_type_navette", string="Shuttle")
    period_id = fields.Many2one('account.period', 'Period', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    dayNum = fields.Char(string="Day", compute="_get_day", store=True)
    active = fields.Boolean()

    report_id = fields.Many2one('oschool.transport.wizard', 'Period', readonly=True)

    h8 = fields.Boolean()
    h12 = fields.Boolean()
    h14 = fields.Boolean()
    h16 = fields.Boolean()

    _defaults = {'active': True,}

    @api.one
    @api.depends('student_id', 'route_id', 'product_id')
    def _get_type_navette(self):
        msg = ""
        for route in self.student_id.route_ids:
            if route.type == 'transport' and route.product_id == self.product_id:
                i = 0
                for bus_schedule in route.bus_schedules:
                    msg = msg + bus_schedule.name + ";"
                    if bus_schedule.name == "8h":
                        self.h8 = True
                        i = i+1
                    if bus_schedule.name == "12h":
                        self.h12 = True
                        i = i+1
                    if bus_schedule.name == "14h":
                        self.h14 = True
                        i = i+1
                    if bus_schedule.name == "16h30":
                        self.h16 = True
                        i = i+1
                break
        if i == 1:
            self.code_navette = "1/2"
        elif i == 2 :
            self.code_navette = "1"
        else:
            self.code_navette = "2"
        self.type_navette = self.route_id.name + ":"+ msg

    @api.one
    @api.depends('day')
    def _get_day(self):
        dayNum = self.day.split("-")
        self.dayNum = str(int(dayNum[2]))

    @api.one
    @api.depends('student_id')
    def _get_phone(self):
        self.phone = self.student_id.parent_id.phone

    @api.one
    @api.depends('route_id')
    def _get_zone(self):
        self.zone_id = self.route_id.zone.id

    @api.one
    def _set_fields(self):
        return True

    def print_transport_report(self, cr, uid, ids, data=None, context=None):

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]

        datas = {
             'ids': ids,
             'model': 'oschool.transport_presence_report',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'oschool.transport.presence',
            'datas': datas,
        }

    def generate_transport_presence(self):
        return True

    # def default_get(self, cr, uid, fields, context=None):
    #     return "test"

    def list_zones(self, cr, uid, context=None):
        ids = self.pool.get('oschool.zone').search(cr,uid,[])
        return self.pool.get('oschool.zone').name_get(cr, uid, ids, context=context)

    def list_periods(self, cr, uid, context=None):
        id = self.pool.get('oschool.academic_year').search(cr,uid,[("state", "=", "current")])
        ids = []
        if id:
            for p in self.pool.get('oschool.academic_year').browse(cr, uid, id).period_ids:
                ids.append(p.id)
            periods = self.pool.get('account.period').name_get(cr, uid, ids, context=context)
            return periods
        else:
            raise exceptions.ValidationError("There is no current academic year!")

    def list_days(self, cr, uid, context=None):
        days = []
        for i in range(1,32):
            days.append((i,str(i)))

        return days

    def print_report(self, cr, uid,current_period,current_zone, context=None):
        report_transport_obj = self.pool.get('oschool.transport.wizard')
        report_ids = report_transport_obj.search(cr, uid, [
            ('zone_id', '=', current_zone),
            ('period_id', '=', current_period),
        ])
        if not report_ids:
            vals= {}
            vals['zone_id'] = current_zone
            vals['period_id'] = current_period
            report_ids = [report_transport_obj.create(cr, uid, vals)]
        else:
            report_transport_obj.unlink(cr, uid,report_ids)
            vals= {}
            vals['zone_id'] = current_zone
            vals['period_id'] = current_period
            report_ids = [report_transport_obj.create(cr, uid, vals)]

        if not report_ids:
            return  {}

        return {
            'type': 'ir.actions.report.xml',
            'report_name':'oschool.report_transport',
            'datas': {
                    'model':'oschool.transport.wizard',
                    'id': report_ids and report_ids[0] or False,
                    'ids': report_ids and report_ids or [],
                    'report_type': 'qweb-html'
                },
            'nodestroy': True
            }

class student_route(models.Model):
    _inherit = 'res.partner'

    route_ids = fields.One2many('pos.order.line', 'student_id', domain=[('type', '=', 'Transport'), ('state_academic_year', '!=', 'closed')], string='Routes')

    state = fields.Char(compute="_get_state")
    @api.one
    @api.depends('academic_year_id')
    def _get_state(self):
        if self.academic_year_id:
            self.state = self.academic_year_id.state
        else:
            self.state = "new"
    def transportation_student(self, cr, uid, ids, context=None):
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
#        if len(pos_line_obj.search(cr, uid, [('student_id', '=', inv.id), ('type', '=', 'transport'), ('academic_year_id', '=', inv.academic_year_id.id)])) > 0:
#            raise osv.except_osv(_('Warning!'), _('Transport already exist for %s.') % inv.academic_year_id.name)

        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_pos_line_generate')
        return {
            'name': _("Generate Transport"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'pos.order.line.generate',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'academic_year_id': inv.academic_year_id.id,
            }
        }

    def list_schedule(self, cr, uid, bus_schedule, context=None):
        if not bus_schedule:
            return []
        result = set()
        for t in bus_schedule:
            result.add(t.id)
        return list(result)


class pos_order_line(models.Model):
    _inherit = "pos.order.line"

    product_id_tmpl = fields.Many2one('product.template', 'Product', domain=[('sale_ok', '=', True)])

    def onchange_oschool_id(self, cr, uid, ids, pricelist_id, product_id, qty, partner_id, student_id):
        if not product_id:
            return {}
        res = self.onchange_product_id(cr, uid, ids, pricelist=pricelist_id, product_id=product_id, qty=1, partner_id=partner_id)
        product = self.pool.get('product.product').browse(cr, uid, product_id)
        student = self.pool.get('res.partner').browse(cr, uid, student_id)
        res['value']['academic_year_id'] = product.pos_categ_id.academic_year.id
        res['value']['period_id'] = self.pool.get('account.period').search(cr, uid, [('code', '=', product.product_tmpl_id.subscription_month)])[0]
        res['value']['group_id'] = student.group_id.id
        res['value']['class_id'] = student.class_id.id
        res['value']['student_id'] = student_id
        res['value']['parent_id'] = partner_id
        res['value']['type'] = product.product_tmpl_id.school_product_type
        return res

    def transport_student(self, cr, uid, ids, context=None):
        if not ids:
            return []
        dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'view_oschool_pos_line_wizard')
        inv = self.browse(cr, uid, ids[0], context=context)
        if inv.order_id:
            raise osv.except_osv(_('Warning!'), _('Please select another line because it have a order.'))
        if inv.period_id.state != 'draft':
            raise osv.except_osv(_('Warning!'), _('Please select another line because period is closed.'))
        return {
            'name': _("Update Transport"),
            'view_mode': 'form',
            'view_id': view_id,
            'view_type': 'form',
            'res_model': 'pos.order.line.update',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': {
                'default_transport_id': inv.product_id.pos_categ_id.id,
                'default_bus_schedule_wizard': [(6, 0, [x.id for x in inv.bus_schedules])],
                'default_subscriber': inv.subscriber,
                'default_discount_transport': inv.discount,
                'academic_year_id': inv.academic_year_id.id,
            }
        }

    def transport_refund(self, cr, uid, ids, context=None):
        if not ids:
            return []
        clone_list = []
        inv = self.browse(cr, uid, ids[0], context=context)
        presence_obj = self.pool.get('oschool.student_transport_presence')
        presence_ids = presence_obj.search(cr, uid, [
                    ('student_id','=',inv.student_id.id),
                    ('period_id','=',inv.period_id.id),
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
        else:
            line_obj = self.pool.get('pos.order.line')
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
                'name': _("Refund Transport"),
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

    subscriber = fields.Boolean("Subscriber", default=1)
    bus_schedules = fields.Many2many('oschool.bus_schedule', 'schedule_pos_line_rel', 'line_id', 'schedule_id', string='Schedules')

class oschool_transport_presence(models.Model):

    _name = "oschool.transport_presence_report"

    name = fields.Char()
    bus_to_zone_id = fields.Many2one('oschool.assign_bus_to_zone', string="Zone")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    transport_presence = fields.One2many("oschool.student_transport_presence", "student_id")

    @api.one
    def _set_fields(self):
        return True


    def print_transport_report(self, cr, uid, ids, data=None, context=None):

        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]

        datas = {
             'ids': ids,
             'model': 'oschool.transport_presence_report',
             'form': data
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'oschool.transport.presence',
            'datas': datas,
        }

    def generate_transport_presence(self):
        return True
