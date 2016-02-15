from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv


class hr_pay_stub(models.Model):
    _name = 'hr.pay.stub'

    name = fields.Many2one('hr.payslip.run','Payslip Batche', required=True, domain=[('state','=','draft')])
    employee_id = fields.Many2one('hr.employee','Employee')
    mode = fields.Selection([('employee', 'By employee'),('category', 'By employee category')], 'Mode', default='employee')
    type = fields.Selection([('input', 'Inputs'),('work', 'Worked Day')], 'Type', required=True, default='input')
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Payroll'))
    hour = fields.Float("Number of hours", digits=(6,3))
    day = fields.Float("Number of days", digits=(6,3))
    rule = fields.Many2one('hr.salary.rule','Salary Rule', required=True, domain="[('category_id.is_stub','=',True)]")
    category = fields.Many2one('hr.employee.category','Employee Category')
    state = fields.Selection(related='name.state', selection=[('draft', 'Draft'), ('close', 'Close')], string="State")

    @api.multi
    def unlink(self):
        for stub in self:
            if stub.state == 'done':
                raise osv.except_osv(_('Warning!'), _('You cannot delete a Stub which is not draft !'))
        return super(hr_pay_stub, self).unlink()

class hr_salary_rule_category(models.Model):
    _inherit = 'hr.salary.rule.category'

    is_stub = fields.Boolean('Is Stub')

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'
   
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=None):
        res = super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)

        if not payslip_run_id:
            return res
            
        stub_obj = self.pool.get('hr.pay.stub')
        contract_obj = self.pool.get('hr.contract')
        obj_emp = self.pool.get('hr.employee')
        
        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            stub_ids = stub_obj.search(cr, uid, [('employee_id', '=', contract.employee_id.id), ('name','=', payslip_run_id), ('mode','=','employee')], context=context)
            for rule in stub_obj.browse(cr, uid, stub_ids, context=context):
                inputs = {
                     'name': rule.rule.name,
                     'code': rule.rule.code,
                     'amount': rule.amount,
                     'contract_id': contract.id,
                 }
                res += [inputs]

            stub_ids = stub_obj.search(cr, uid, [('name','=', payslip_run_id), ('mode','=','category')], context=context)
            for rule in stub_obj.browse(cr, uid, stub_ids, context=context):
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [rule.category.id])])
                if contract.employee_id.id in emp_ids:
                    inputs = {
                     'name': rule.rule.name,
                     'code': rule.rule.code,
                     'amount': rule.amount,
                     'contract_id': contract.id,
                     }
                    res += [inputs]
        return res
       
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=None):
        
        res = super(hr_payslip, self).get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)
        
        stub_obj = self.pool.get('hr.pay.stub') 
        obj_emp = self.pool.get('hr.employee')

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            stub_ids = stub_obj.search(cr, uid, [('employee_id', '=', contract.employee_id.id), ('name','=', payslip_run_id), ('mode','=','employee')], context=context)
            for rule in stub_obj.browse(cr, uid, stub_ids, context=context):
                if rule.type == 'work':
                    input_worked_days = {
                         'name':rule.rule.name,
                         'sequence': 1,
                         'code': rule.rule.code,
                         'number_of_days': rule.day,
                         'number_of_hours':rule.hour,
                         'contract_id': contract.id,
                    }
            
                    res += [input_worked_days]
                                        
            stub_ids = stub_obj.search(cr, uid, [('name','=', payslip_run_id), ('mode','=','category')], context=context)
            for rule in stub_obj.browse(cr, uid, stub_ids, context=context):
                emp_ids = obj_emp.search(cr, uid, [('category_ids', 'child_of', [rule.category.id])])
                if contract.employee_id.id in emp_ids:
                    if rule.type == 'work':
                        input_worked_days = {
                            'name':rule.rule.name,
                            'sequence': 1,
                            'code': rule.rule.code,
                            'number_of_days': rule.day,
                            'number_of_hours':rule.hour,
                            'contract_id': contract.id,
                        }
                        res += [input_worked_days]
                    
        return res


 

 
 
    
    
