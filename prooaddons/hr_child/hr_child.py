from openerp import models, fields, api
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class hr_child(models.Model):
    _name = 'hr.child'
    _order = "name, rank"  

    name = fields.Many2one('hr.employee', 'Employee')
    rank = fields.Integer('Rank')
    child_name = fields.Char('Name', size=64, required=True)
    birth = fields.Date('Birthday', required=True)
    supported = fields.Boolean('Supported')
    scholar = fields.Boolean('Scholarship holder')
    hand = fields.Boolean('Handicapped')
    amount = fields.Float('Amount',  digits_compute=dp.get_precision('Account'))
    
    @api.model
    def create(self, vals):
        emp = self.env["hr.employee"].browse(vals['name'])
        deduction_id = self.env["hr.deduction"].search([])
        if not deduction_id:
            raise osv.except_osv(_("Warning !"), _("You must define the deductions !"))
                               
        rank = len(emp.childs_ids) + 1
        vals.update({'rank': rank})
        
        if rank == 1:
            vals['amount'] = deduction_id.first_child
        if rank == 2:
            vals['amount'] = deduction_id.second_child
        if rank == 3 :
            vals['amount'] = deduction_id.third_child
        if rank == 4 :
            vals['amount'] = deduction_id.fourth_child
        
        childs = self.search([('name','=', vals['name']), ('supported', '=', True)])
        employee = self.env['hr.employee'].browse(vals['name'])
        employee.write({'children': len(childs)})
        
        return super(hr_child, self).create(vals)

    @api.multi
    def write (self, data):
    	childs = self.search([('name', '=', data['name']), ('supported', '=', True)])
        employee = self.env['hr.employee'].browse(data['name'])
        employee.write({'children': len(childs)})
        return super(hr_child, self).write(data)

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    def _child_amount(self):
        self.amount_child = 0.0
        if self.householder == True:
            for child in self.childs_ids:
                if child.supported:
                    self.amount_child += child.amount

    childs_ids = fields.One2many('hr.child', 'name', 'Child')
    householder = fields.Boolean('Householder')
    amount_child = fields.Float(string='Total Child Amount', digits_compute=dp.get_precision('Account'), readonly=True, compute='_child_amount')
 
class child_amount(models.Model):
    _name = 'hr.deduction'

    name = fields.Float('Householder', digits_compute=dp.get_precision('Account'))
    first_child = fields.Float('First Child Amount', digits_compute=dp.get_precision('Account'))
    second_child = fields.Float('Second Child Amount', digits_compute=dp.get_precision('Account'))
    third_child = fields.Float('Third Child Amount', digits_compute=dp.get_precision('Account'))
    fourth_child = fields.Float('Fourth Child Amount', digits_compute=dp.get_precision('Account'))


class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    householder = fields.Boolean(related='employee_id.householder', string='Householder', store=True)

