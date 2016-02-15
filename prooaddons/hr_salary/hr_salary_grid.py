#-*- coding:utf-8 -*-
from openerp import models, fields, api, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta

class hr_salary(models.Model):
    _name = 'hr.salary'  

    name = fields.Char('Name', size=64, required=True)
    active = fields.Boolean('Active', default=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date')
    salary_ids = fields.One2many('hr.salary.grid', 'grid', 'Classifications')

    _defaults = {
        'start_date': lambda *a: time.strftime('%Y-%m-%d'),
        }

class hr_salary_grid(models.Model):
    _name = 'hr.salary.grid'

    grid = fields.Many2one('hr.salary','Salary Grid')
    name = fields.Char('Classification', size=64, required=True)
    category = fields.Char('Category', size=64, required=True)
    echelon = fields.Char('Echelon', size=64, required=True)
    amount = fields.Float('Amount',  digits_compute=dp.get_precision('Account'), required=True)
    duration = fields.Integer('Duration', required=True)
    parent_id = fields.Many2one('hr.salary.grid', 'Classification Before', select=True)
    children_ids = fields.One2many('hr.salary.grid', 'parent_id', 'Following')

class hr_employee_grid(models.Model):
    _name = "hr.employee.grid"
    _description = "Employee Salary Grid History"
    _order = 'date_approval desc'

    def unlink(self):
        for rec in self:
            raise osv.except_osv(_('Warning!'), _('You can not delete history!'))
        return super(hr_employee_grid, self).unlink()

    name = fields.Char('Name', size=128, required=True)
    classification = fields.Many2one('hr.salary.grid', 'Classification', required=True)
    grid = fields.Many2one(related='classification.grid', relation='hr.salary', string='Salary Grid', store=True)
    amount = fields.Float(related='classification.amount', string='Amount', store=True)
    date_approval = fields.Date('Date Approval', required=True)
    employee_id = fields.Many2one("hr.employee", 'Employee', required=True)

    _defaults = {
        'date_approval': lambda *a: time.strftime('%Y-%m-%d'),
        }

class hr_employee(models.Model):
    _inherit='hr.employee'

    grid = fields.Many2one('hr.salary', 'Salary Grid')
    classification = fields.Many2one('hr.salary.grid','Classification')
    history_ids = fields.One2many("hr.employee.grid", "employee_id", "History salary grid")

class hr_contract(models.Model):
    _inherit = 'hr.contract'

    grid = fields.Many2one('hr.salary','Salary Grid')
    classification = fields.Many2one('hr.salary.grid','Classification')

    @api.multi
    def classification_change(self, classification):
        if classification :
            return {'value':{'wage': self.env['hr.salary.grid'].browse(classification).amount}}
        return {}

    @api.multi
    def grid_change(self, grid, classification):
        if classification:
            return {'value': {'classification': False}}
        return {}

    @api.model
    def create(self, data):
        if 'grid' in data and data['grid'] and 'classification' in data and data['classification']:
            employee = self.env['hr.employee'].browse(data['employee_id'])
            employee.write({'grid':data['grid'],'classification':data['classification']})
            grid_obj = self.env['hr.employee.grid']
            part = self.env['hr.salary.grid'].browse(data['classification'])
            res = {
                'name': _('Contract N° %s') % (data['name']),
                'classification': part.id,
                'date_approval': data['date_start'],
                'employee_id': data['employee_id'],
                }
            grid_obj.create(res)
        return super(hr_contract, self).create(data)

    @api.multi
    def write(self, data):
        employee_obj = self.env['hr.employee']
        for contract in self:
            contract.employee_id.write({'grid':data.get('grid', False) and data['grid'] or contract.grid.id,'classification':data.get('classification', False) and data['classification'] or contract.classification.id})
        return super(hr_contract, self).write(data)

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'
     
    def close_payslip_run(self, cr, uid, ids, context=None):
         res = {}
         employee_grid_obj = self.pool.get('hr.employee.grid')
         for payslip in self.browse(cr, uid, ids, context=context).slip_ids:
             if not payslip.employee_id.classification:
                 continue
             limit_date =  str(datetime.strptime(payslip.date_to, '%Y-%m-%d') + relativedelta(months=+2, day=1, days=-1))[:10]
             duration = payslip.employee_id.classification.duration
             history_id = employee_grid_obj.search(cr, uid, [('employee_id', '=', payslip.employee_id.id)], limit=1, order='date_approval desc')
             last_date = employee_grid_obj.browse(cr, uid, history_id, context=context).date_approval
             employee_date = datetime.strptime(last_date, '%Y-%m-%d') + relativedelta(months=duration)
             if employee_date <= limit_date:
                new_class = payslip.employee_id.classification.children_ids[0]
                res = {
                'name':_('Seniority'),
                'classification': new_class.classification.id,
                'date_approval': employee_date,
                'employee_id': payslip.employee_id.id,
                    }
                employee_grid_obj.create(cr, uid, res, context=context)
                self.pool.get('hr.employee').write(cr, uid, payslip.employee_id.id, {'grid': new_class.grid.id, 'classification': new_class.classification.id})
         return super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context=context)

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    grid = fields.Many2one(related='employee_id.grid', relation='hr.salary', string='Salary Grid', store=True)
    classification = fields.Many2one(related='employee_id.classification', relation='hr.salary.grid', string='Classification', store=True)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
