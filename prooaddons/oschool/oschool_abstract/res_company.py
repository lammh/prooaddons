from openerp import models, fields, api, _

class res_company(models.Model):
    _inherit = "res.company"

    activate_check_minimum_age_registration = fields.Boolean(string="Activate Checking Minimum age registration for this company")