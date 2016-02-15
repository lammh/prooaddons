# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from openerp import models, fields, api, exceptions, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
import time
import tools



class academic_year(models.Model):
    _name = 'oschool.academic_year'
    _rec_name = 'code'

    name = fields.Char(string="Designation", required=True)
    code = fields.Char(string="Code", required=True)
    date_start = fields.Date(string="Start Date", required=True)
    date_stop = fields.Date(string="End Date", required=True)
    period_ids = fields.Many2many('account.period', string="Period")
    company_id = fields.Many2one('res.company', 'Company')
    state = fields.Selection([
                                 ('new', "New"),
                                 ('current', "Current"),
                                 ('closed', "Closed"),
                             ], default='new')


    def _generate_periods(self,cr,uid, date_start,date_stop, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        periods = self.pool.get('account.period').search(cr,uid,[('date_start','>=',date_start),('date_start','<=',date_stop), ('code','not ilike','00'),('company_id','=',current_user.company_id.id)])
        tmp =[]
        for period in periods:
            tmp.append(period)
        return [[6, False, tmp]]

    def create(self, cr, uid, vals, context=None):

        date_start = datetime.strptime(vals['date_start'], '%Y-%m-%d')
        date_stop = datetime.strptime(vals['date_stop'], '%Y-%m-%d')
        dat_start = "%s-%s-01" % (date_start.year,date_start.month)
        date_stop = "%s-%s-01" % (date_stop.year,date_stop.month)
        vals['period_ids'] = self._generate_periods(cr,uid,dat_start,date_stop)
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        current = self.search(cr, uid, [('state', '=', 'new'),('company_id','=', current_user.company_id.id)], context=context)
        if len(current) > 0:
            raise ValidationError("School year with the new state already exist")
        new_id = super(academic_year, self).create(cr, uid, vals, context=context)
        return new_id


    def write(self, cr, uid, ids, values, context = None):

        if values.has_key('date_start'):
            date_start = datetime.strptime(values['date_start'], '%Y-%m-%d')
        else:
            for fy in self.browse(cr, uid, ids, context=context):
                date_start = datetime.strptime(fy.date_start, '%Y-%m-%d')
        if values.has_key('date_stop'):
            date_stop = datetime.strptime(values['date_stop'], '%Y-%m-%d')
        else:
            for fy in self.browse(cr, uid, ids, context=context):
                date_stop = datetime.strptime(fy.date_stop, '%Y-%m-%d')

        dat_start = "%s-%s-01" % (date_start.year,date_start.month)
        date_stop = "%s-%s-01" % (date_stop.year,date_stop.month)
        values['period_ids'] =  self._generate_periods(cr,uid,dat_start,date_stop)
        res = super(academic_year, self).write(cr, uid, ids, values, context = context)
        return res


    def action_new(self, cr, uid, ids, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        current = self.search(cr, uid, [('state', '=', 'new'),('company_id','=',current_user.company_id.id)])
        if len(current) > 0:
            raise ValidationError("School year with the new state already exist")
        return self.write(cr, uid, ids, {'state': 'new'})

    def action_current(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'current'})

    def action_closed(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'closed'})

    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code,company_id)',
         "The code must be unique"),
        ('name_unique',
         'UNIQUE(name,company_id)',
         "The name must be unique"),
        ('check_date',
         'CHECK(date_start < date_stop)',
         "Start Date Must be Below End Date"),
    ]

    _defaults = {
        'company_id': tools.get_default_company,
    }

class groups(models.Model):
    _name = 'oschool.groups'

    name = fields.Char(string="Group designation", required=True)
    code = fields.Char(string="Code", required=True)
    number_of_places = fields.Integer(string="Number of places", required=True)
    class_ids = fields.One2many('oschool.classes', 'code', 'Classes')
    seq = fields.Integer(string="Sequence",required=True, help="This field determine the order of the groups, is required for transport report")
    company_id = fields.Many2one('res.company', 'Company')

    _defaults = {
        'company_id': tools.get_default_company,
    }

    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code,company_id)',
         "Group code must be unique"),
        ('name_unique',
         'UNIQUE(name,company_id)',
         "The name must be unique"),
        ('seq_unique',
         'UNIQUE(seq)',
         "Group sequence must be unique")
    ]


class classes(models.Model):
    _name = 'oschool.classes'

    name = fields.Char(string="Classroom designation", required=True)
    code = fields.Char(string="Code", required=True)
    group = fields.Many2one('oschool.groups', 'Groupe', ondelete='cascade')
    company_id = fields.Many2one('res.company', 'Company')


    _defaults = {
        'company_id': tools.get_default_company,
    }
    _sql_constraints = [
        ('code_unique',
         'UNIQUE(code,company_id)',
         "Le code de la classe doit etre unique"),
        ('name_unique',
         'UNIQUE(name,company_id)',
         "The name must be unique")
    ]


class pos_category(models.Model):
    _inherit = 'pos.category'

    price = fields.Float(string="Price")
    place_number = fields.Integer(string="place number")
    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")
    start_date_registration = fields.Date(string='Start Registration Date')
    stop_date_registration = fields.Date(string='End Registration Date')
    date_start = fields.Date(string='Start Date')
    date_stop = fields.Date(string='End Date')
    services_ids = fields.One2many('product.template', 'pos_categ_id', ondelete='cascade', string='Months')
    product_category = fields.Many2one('product.category', string="Category Type")
    cash = fields.Boolean(default=False, string="Cash")
    school_product_type = fields.Selection(
        [('service', 'Service'), ('registration', 'Registration'), ('club', 'Club'), ('event', 'Event'),
         ('study', 'Study'), ('extra', 'Extra'), ('transport', 'Transport')])
    groups = fields.Many2one('oschool.groups', 'Groupe', ondelete='cascade')
    excluded_services_ids = fields.Many2many('pos.category', 'service_category_rel', 'category_id', 'service_id', string='Excluded services')
    company_id = fields.Many2one('res.company', 'Company')

    @api.one
    @api.onchange('academic_year')
    def _set_start_stop_date(self):
        self.date_start = self.academic_year.date_start
        self.date_stop = self.academic_year.date_stop

    _sql_constraints = [
        ('check_date',
         'CHECK(date_start <= date_stop)',
         "Start Date Must be Below End Date"),
        ('check_registration_date',
         'CHECK(start_date_registration < stop_date_registration)',
         "Start Date Registration Must be Below End Date registration"),
        ('check_registration_date_stop_date',
         'CHECK(stop_date_registration <= date_stop)',
         "Stop Date Registration Must be Below End Date"),
        ('name_unique',
         'UNIQUE(name,academic_year)',
         "This record already exists for this academic year"),
    ]


    _defaults = {
        'company_id': tools.get_default_company,
    }

    def generate_months_clubs(self, cr, uid, ids, context=None, interval=1):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        property_account_income_extra = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050005'),('company_id','=',company_id)])
        if not property_account_income_extra:
            raise ValidationError("There is not account with code 7050005")
        period_obj = self.pool.get('product.template')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': "%s %s" % (fy.name, ds.strftime('%m/%Y')),
                    'pos_categ_id': fy.id,
                    'type': 'service',
                    'available_in_pos': True,
                    'property_account_income': property_account_income_extra[0],
                    'list_price': fy.price,
                    'subscription_month': ds.strftime('%m/%Y'),
                    'school_product_type': fy.school_product_type,
                    'academic_year': fy.academic_year.id,
                    'categ_id': fy.product_category.id,
                    'cash': fy.cash,
                    'company_id': fy.company_id.id,
                })
                ds = ds + relativedelta(months=interval)
        return True

    def generate_inscriptions(self, cr, uid, ids, context=None, interval=1):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        property_account_income_inscription = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050004'),('company_id','=',company_id)])
        if not property_account_income_inscription:
            raise ValidationError("There is not account with code 7050004")
        period_obj = self.pool.get('product.template')
        sequence = 1
        for fy in self.browse(cr, uid, ids, context=context):
            if (fy.academic_year.state) == "current" or (fy.academic_year.state) == "closed":
                error = "You cannot generate inscriptions year that have '%s' status" % _(fy.academic_year.state)
                raise ValidationError(error)
            period_obj.create(cr, uid, {
                'name': "%s %s" % (_("Inscription"), fy.academic_year.code),
                'pos_categ_id': fy.id,
                'type': 'service',
                'available_in_pos': True,
                'property_account_income': property_account_income_inscription[0],
                'school_product_type': fy.school_product_type,
                'academic_year': fy.academic_year.id,
                'categ_id': fy.product_category.id,
                'inscription_sequence': sequence,
            })
            sequence = sequence + 1
            period_obj.create(cr, uid, {
                'name': "%s %s" % (_("Rénscription"), fy.academic_year.code),
                'pos_categ_id': fy.id,
                'type': 'service',
                'available_in_pos': True,
                'property_account_income': property_account_income_inscription[0],
                'school_product_type': fy.school_product_type,
                'academic_year': fy.academic_year.id,
                'categ_id': fy.product_category.id,
                'inscription_sequence': sequence,
            })


    def generate_months_study(self, cr, uid, ids, context=None, interval=1):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        property_account_income = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050001'),('company_id','=',company_id)])
        if not property_account_income:
            raise ValidationError("There is not account with code 7050001")
        period_obj = self.pool.get('product.template')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.academic_year.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.academic_year.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > fy.academic_year.date_stop:
                    de = datetime.strptime(fy.academic_year.date_stop, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': "%s %s" % (fy.name, ds.strftime('%m/%Y')),
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



    def generate_months_service(self, cr, uid, ids, context=None, interval=1):
        company_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        property_account_income = self.pool.get('account.account').search(cr, uid, [('code', '=', '7050002'),('company_id','=',company_id)])
        if not property_account_income:
            raise ValidationError("There is not account with code 7050002")
        period_obj = self.pool.get('product.template')
        for fy in self.browse(cr, uid, ids, context=context):
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=interval, days=-1)
                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create(cr, uid, {
                    'name': "%s %s" % (fy.name, ds.strftime('%m/%Y')),
                    'pos_categ_id': fy.id,
                    'type': 'service',
                    'available_in_pos': True,
                    'list_price': fy.price,
                    'property_account_income': property_account_income[0],
                    'subscription_month': ds.strftime('%m/%Y'),
                    'school_product_type': fy.school_product_type,
                    'categ_id': fy.product_category.id,
                    'academic_year': fy.academic_year.id,
                    'cash': fy.cash,
                })
                ds = ds + relativedelta(months=interval)

    def unlink(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        product_tmpl_obj = self.pool.get('product.template')
        pos_order_line_obj = self.pool.get('pos.order.line')
        for id in ids:
            category = self.browse(cr, uid, id)
            product_tmpl_ids = product_tmpl_obj.search(cr, uid,
                                    [('pos_categ_id','=',id),
                                     ('school_product_type','=',category.school_product_type)])

            for product_tmpl_id in product_tmpl_ids:
                product_ids = product_obj.search(cr, uid,[('product_tmpl_id','=',product_tmpl_id)])
                for product_id in product_ids:
                    pos_order_line_ids = pos_order_line_obj.search(cr, uid,[('product_id','=',product_id)])
                    if pos_order_line_ids:
                        #product = product_obj.browse(cr, uid, product_id)
                        msg = "One or more command was created for the category {0}.".format(category.name)
                        raise exceptions.Warning(msg)
                        return False
            product_tmpl_obj.unlink(cr, uid, product_tmpl_ids, context)
            super(pos_category, self).unlink(cr, uid, id, context)
        return True

class product_template(models.Model):
    _inherit = 'product.template'

    subscription_month = fields.Char(string='Subscription Month')
    cash = fields.Boolean(default=False, string="Cash")
    school_product_type = fields.Selection(
        [('service', 'Service'), ('registration', 'Registration'), ('club', 'Club'), ('event', 'Event'),
         ('study', 'Study'), ('extra', 'Extra'), ('transport', 'Transport')])
    inscription_sequence = fields.Integer(string="sequence")


class hr_employee(models.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _description = 'Driver Information'

    licence_no = fields.Char(string='Licence No', size=50)
    company_id = fields.Many2one('res.company', 'Company')


    _defaults = {
        'company_id': tools.get_default_company,
    }


class parents_categories(models.Model):
    _inherit = 'product.pricelist.item'

    _defaults = {
        'base': 1,
    }

class oschool_account_journal(models.Model):
    _inherit = 'account.journal'

    cash = fields.Boolean(default=False, string="Cash")
    registration = fields.Boolean(default=False, string="Registration")
    extra = fields.Boolean(default=False, string="Extra")
    is_check = fields.Boolean(default=False, string="Is check")


class pos_session_opening(osv.osv_memory):
    _inherit = 'pos.session.opening'

    company_id = fields.Many2one('res.company', 'Company')

    _defaults = {
        'company_id': tools.get_default_company,
    }
    def oschool_open_session_cb(self, cr, uid, ids, context=None):
        assert len(ids) == 1, "you can open only one session at a time"
        proxy = self.pool.get('pos.session')
        wizard = self.browse(cr, uid, ids[0], context=context)
        if not wizard.pos_session_id:
            values = {
                'user_id': uid,
                'config_id': wizard.pos_config_id.id,
            }
            session_id = proxy.create(cr, uid, values, context=context)
            s = proxy.browse(cr, uid, session_id, context=context)
            if s.state == 'opened':
                return self.oschool_open_ui(cr, uid, ids, context=context)
            return self._open_session(session_id)
        return self._open_session(wizard.pos_session_id.id)

    def oschool_open_ui(self, cr, uid, ids, context=None):
        data = self.browse(cr, uid, ids[0], context=context)
        context = dict(context or {})
        context['active_id'] = data.pos_session_id.id
        obj = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'main_oschool_menu')[1]
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': obj},
        }


    def oschool_open_existing_session_cb_close(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        wizard.pos_session_id.signal_workflow('cashbox_control')
        return self.oschool_open_session_cb(cr, uid, ids, context)


    def oschool_open_session_cb(self, cr, uid, ids, context=None):

        view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'oschool_pos_session_form')

        assert len(ids) == 1, "you can open only one session at a time"
        proxy = self.pool.get('pos.session')
        wizard = self.browse(cr, uid, ids[0], context=context)
        if not wizard.pos_session_id:
            values = {
                'user_id': uid,
                'config_id': wizard.pos_config_id.id,
            }
            session_id = proxy.create(cr, uid, values, context=context)
            s = proxy.browse(cr, uid, session_id, context=context)
            if s.state == 'opened':
                return self.oschool_open_ui(cr, uid, ids, context=context)
            return self._oschool_open_session(session_id, view_id, context)
        return self._oschool_open_session(wizard.pos_session_id.id, view_id,context)

    def _oschool_open_session(self, session_id, view_id, context):

        return {
            'name': _('Session'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'pos.session',
            'res_id': session_id,
             # 'view_id': [view_id],
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


class pos_session(osv.osv):

    _inherit = 'pos.session'

    company_id = fields.Many2one('res.company', 'Company')

    _defaults = {
        'company_id': tools.get_default_company,
    }

    def wkf_action_close(self, cr, uid, ids, context=None):
        # Close CashBox
        for record in self.browse(cr, uid, ids, context=context):
            for st in record.statement_ids:
                if abs(st.difference) > st.journal_id.amount_authorized_diff:
                    # The pos manager can close statements with maximums.
                    if not self.pool.get('ir.model.access').check_groups(cr, uid, "point_of_sale.group_pos_manager"):
                        raise osv.except_osv(_('Error!'),
                                             _(
                                                 "Your ending balance is too different from the theoretical cash closing (%.2f), the maximum allowed is: %.2f. You can contact your manager to force it.") % (
                                             st.difference, st.journal_id.amount_authorized_diff))
                if (st.journal_id.type not in ['bank', 'cash']):
                    raise osv.except_osv(_('Error!'),
                                         _("The type of the journal for your payment method should be bank or cash "))
                getattr(st, 'button_confirm_%s' % st.journal_id.type)(context=context)
        self._confirm_orders(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'closed'}, context=context)

        obj = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'main_oschool_menu')[1]
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': obj},
        }


    def open_frontend_cb(self, cr, uid, ids, context=None):
        if not context:
            context = {}
        if not ids:
            return {}
        for session in self.browse(cr, uid, ids, context=context):
            if session.user_id.id != uid:
                raise osv.except_osv(
                    _('Error!'),
                    _(
                        "You cannot use the session of another users. This session is owned by %s. Please first close this one to use this point of sale." % session.user_id.name))
        context.update({'active_id': ids[0]})
        obj = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool', 'main_oschool_menu')[1]
        return {
            'type': 'ir.actions.client',
            'name': 'Point of Sale Menu',
            'tag': 'reload',
            'params': {'menu_id': obj},
        }


class product_template(models.Model):
    _inherit = 'product.template'

    academic_year = fields.Many2one('oschool.academic_year', ondelete='cascade', string="Academic year")

    _sql_constraints = [
        ('unique_oschool_product', 'unique(academic_year,company_id, school_product_type, subscription_month, pos_categ_id)',
         'The record must be unique by year'),
        ('unique_oschool_inscription_by_year',
         'unique(academic_year, company_id,school_product_type, inscription_sequence, categ_id)',
         'The registration must be unique by year')
    ]