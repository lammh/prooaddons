from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    type = fields.Selection([('monthly', 'Monthly'),('hourly','Hourly')],'Type', required=True, default='monthly')
    number_of_hours = fields.Float('Number of hours', required=True)
    number_of_days = fields.Float('Number of days', required=True)

class hr_contract_type(models.Model):
    _inherit = 'hr.contract.type'

    employee_cnss = fields.Float('Empoyee CNSS',  digits_compute=dp.get_precision('Discount'))
    boss_cnss = fields.Float('Employer CNSS',  digits_compute=dp.get_precision('Discount'))
    foprolos = fields.Float('Foprolos',  digits_compute=dp.get_precision('Discount'))
    tfp = fields.Float('TFP',  digits_compute=dp.get_precision('Discount'))
    exploit_code = fields.Char('Exploit Code', size=8, required=True)
    taxable = fields.Boolean('Taxable')

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    wage = fields.Float('Wage', digits_compute=dp.get_precision('Payroll'), required=True, help="Basic Salary of the employee")
    employee_cnss = fields.Float(related='type_id.employee_cnss', string="Empoyee CNSS")
    boss_cnss = fields.Float(related='type_id.boss_cnss', string="Employer CNSS")
    foprolos = fields.Float(related='type_id.foprolos', string="Foprolos")
    tfp = fields.Float(related='type_id.tfp', string="TFP")
    exploit_code = fields.Char(related='type_id.exploit_code', string="Exploit Code")
    taxable = fields.Boolean(related='type_id.taxable', string="Taxable")

class employer(models.Model):
    _inherit = "hr.employee"
    _order = "matricule"

    @api.multi
    @api.depends('name', 'matricule')
    def name_get(self):
        res = []
        for line in self:
            if line.matricule:
                res.append((line.id, '(' + line.matricule + ') ' + line.name))
            else:
                res.append((line.id, line.name))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('matricule', operator, name)]+ args, limit=limit)
            if not recs:
                recs = self.search([('name', operator, name)]+ args, limit=limit)
        else:
            recs = self.search(args, limit=limit)
        return recs.name_get()

    matricule = fields.Char("Matricule")
