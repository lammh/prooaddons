# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
import time
from openerp.exceptions import ValidationError
from openerp.osv import osv
from openerp import SUPERUSER_ID


class base_config_settings(osv.TransientModel):

    _name = "oschool.config.settings"
    _inherit = 'res.config.settings'


    registration_min_age_year = fields.Integer(string="Minimum number of years", required=True, default=5)
    registration_min_age_month = fields.Integer(string="Minimum number of months", required=True, default=6)
    pay_septembre_juin_together = fields.Boolean(string="Pay first and last periods together")
    check_minimum_age_registration = fields.Boolean(string="Check Minimum age registration")

    def execute(self, cr, uid, ids, context=None):
        admin_group = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'oschool','oschool_group_admin_scolarity')[1]
        groups_id = self.pool.get("res.users").browse(cr, uid, uid).groups_id
        is_admin = False
        for group in groups_id:
            if group.id == admin_group:
                is_admin = True
                break
        if is_admin:
            uid = SUPERUSER_ID
        return super(base_config_settings, self).execute(cr, uid, ids, context)

    def set_registration_min_age_year(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "oschool.config.registration_min_age_year", record.registration_min_age_year or '', context=context)

    def get_default_registration_min_age_year(self, cr, uid, ids, context=None):
        registration_min_age_year = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.registration_min_age_year", default=5, context=context)
        return {'registration_min_age_year': int(registration_min_age_year)}


    def set_registration_min_age_month(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "oschool.config.registration_min_age_month", record.registration_min_age_month or '', context=context)

    def set_check_minimum_age_registration(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "oschool.config.check_minimum_age_registration", record.check_minimum_age_registration or '', context=context)


    def get_default_check_minimum_age_registration(self, cr, uid, ids, context=None):
        check_minimum_age_registration = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.check_minimum_age_registration", default=None, context=context)
        return {'check_minimum_age_registration': check_minimum_age_registration or False}


    def get_default_registration_min_age_month(self, cr, uid, ids, context=None):
        registration_min_age_month = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.registration_min_age_month", default=6, context=context)
        return {'registration_min_age_month': int(registration_min_age_month)}

    def __set_pay_septembre_juin_together(self, cr, uid, ids, context=None):

        config_parameters = self.pool.get("ir.config_parameter")
        for record in self.browse(cr, uid, ids, context=context):
            config_parameters.set_param(cr, uid, "oschool.config.pay_septembre_juin_together", record.pay_septembre_juin_together or '', context=context)


    def get_default_pay_septembre_juin_together(self, cr, uid, ids, context=None):
        pay_septembre_juin_together = self.pool.get("ir.config_parameter").get_param(cr, uid, "oschool.config.pay_septembre_juin_together", default=None, context=context)
        return {'pay_septembre_juin_together': pay_septembre_juin_together or False}




    @api.one
    @api.constrains('registration_min_age_month')
    def check_month_lenght(self):
        if self.registration_min_age_month:
            if (self.registration_min_age_month > 12) or (self.registration_min_age_month < 1) or (self.registration_min_age_month == False):
                raise ValidationError("Month must be between 1 and 12")