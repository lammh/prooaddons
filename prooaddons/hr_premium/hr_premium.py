from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class hr_salary_rule_category(models.Model):
    
    _inherit = 'hr.salary.rule.category'

    is_prime = fields.Boolean('Is Prime')


class hr_premium_type(models.Model):
    _name = 'hr.premium.type'

    @api.multi
    @api.depends('name')
    def name_get(self):
        res = []
        for line in self:
            res.append((line.id, '(' + line.name.code + ') ' + line.name.name))
        return res

    name = fields.Many2one('hr.salary.rule','Salary Rule', required=True, domain="[('category_id.is_prime','=',True)]")
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True)

class hr_employee_premium(models.Model):
    _name = 'hr.employee.premium'

    name = fields.Many2one('hr.employee', 'Employee',required=True)
    premium = fields.Many2one('hr.premium.type', 'Premium Type', required=True)
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True)

    @api.multi
    def premium_change(self, premium, context=None):
        if premium :
            return {'value': {'amount': self.env['hr.premium.type'].browse(premium).amount}}
        return {}

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    premium_ids = fields.One2many('hr.employee.premium', 'name', 'Premium')
 
class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
   
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=None):
        res = super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)

        premium_obj = self.pool.get('hr.employee.premium')    
        contract_obj = self.pool.get('hr.contract')

        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            prem_ids = premium_obj.search(cr, uid, [('name', '=', contract.employee_id.id)], context=context)
            for rule in premium_obj.browse(cr, uid, prem_ids, context=context):
                inputs = {
                          'name': rule.premium.name.name,
                          'code': rule.premium.name.code,
                          'amount': rule.amount,
                          'contract_id': contract.id,
                         }
                res += [inputs]
        return res

