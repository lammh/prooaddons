from openerp import models, fields, api, _
from openerp.osv import osv
import time
from datetime import date
from dateutil import relativedelta
import openerp.addons.decimal_precision as dp

class hr_loan(models.Model):
    _name = 'hr.loan'

    @api.multi
    def write(self, vals):
        loan_details_obj = self.env['hr.loan.detail']
        prec = self.env['decimal.precision'].precision_get('Account')
        id = super(hr_loan, self).write(vals)
        for loan in self:
            if loan.state == 'accepted' and not vals.get('state', False):
                value = {}
                base = round(loan.amount / loan.period, prec)
                benefit = round((loan.amount / loan.period) * loan.rate, prec)
                for i in range(loan.period):
                    value = {
                             'name': loan.description + ' ' + str((date(*time.strptime(str(loan.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+i)).strftime('%Y-%m')),
                             'start_date': str((date(*time.strptime(str(loan.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+i)).strftime('%Y-%m-%d')),
                             'base': base,
                             'benefit': benefit,
                             'total': base + benefit,
                             'state': "draft",
                             'loan_id': loan.id,
                             }
                    loan_details_obj.create(value)
            return id

    @api.multi
    def accepted_loan(self):
        if not self.period  or not self.start_date :
            raise osv.except_osv(_('Warning!'), _('You cannot accept a loan without defining the rate, the period and the start date !'))
        self.state = 'accepted'
        return True

    @api.multi
    def refused_loan(self):
        self.state = 'refused'
        for detail in self.detail_ids:
            detail.unlink()
        return True

    @api.multi
    def anticipate_loan(self):
        self.state = 'done'
        for detail in self.detail_ids:
            detail.state = 'done'
        return True

    @api.multi
    def simulate_loan(self):
        sum = 0
        sum1 = 0
        sum2 = 0
        prec = self.env['decimal.precision'].precision_get('Account')
        value = {}
        if self.period and self.start_date :
            for detail in self.detail_ids:
                detail.unlink()
            base = round(self.amount / self.period, prec)
            benefit = round((self.amount / self.period) * self.rate, prec)
            for i in range(self.period - 1):
                value = {
                    'name': self.description +' ' + str((date(*time.strptime(str(self.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+i)).strftime('%Y-%m')),
                    'start_date': str((date(*time.strptime(str(self.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+i)).strftime('%Y-%m-%d')),
                    'base': base,
                    'benefit': benefit,
                    'total': base + benefit,
                    'state': "draft",
                    'loan_id': self.id,
                         }
                sum += base
                sum1 += benefit
                sum2 += base + benefit
                self.env['hr.loan.detail'].create(value)
            value = {
                    'name': self.description +' ' + str((date(*time.strptime(str(self.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+i +1)).strftime('%Y-%m')),
                    'start_date': str((date(*time.strptime(str(self.start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+ i+ 1)).strftime('%Y-%m-%d')),
                    'base': self.amount-sum,
                    'benefit': round(self.amount * self.rate, prec)-sum1,
                    'total': (self.amount+(self.amount*self.rate))-sum2,
                    'state': "draft",
                    'loan_id': self.id,
                         }
            self.env['hr.loan.detail'].create(value)
        return True

    @api.multi
    def unlink (self):
        for loan in self:
            if loan.state != 'draft':
                raise osv.except_osv(_('Warning!'),_('You cannot delete this loan !'))
        for detail in self.detail_ids:
            detail.unlink()
        return super(hr_loan, self).unlink()

    @api.multi
    def onchange_date(self, period, start_date):
        v = {}
        if not period:
            return {'value': v}
        if not start_date:
            return {'value': v}
        v['end_date'] = str(date(*time.strptime(str(start_date),'%Y-%m-%d')[:3]) + relativedelta.relativedelta(months=+period, day=1, days=0))[:10]
        return {'value': v}
       
    name = fields.Char('Number', size=64, readonly=True)
    description = fields.Char('Description', size=128)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    loan_date = fields.Date('Approval Date', required=True, default=date.today())
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'), required=True)
    period = fields.Integer('Period')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    rate = fields.Float('Rate', digits_compute=dp.get_precision('Discount'), help="A rate of 0.08 is equal to 8 %")
    rule_id = fields.Many2one('hr.salary.rule', 'Loan Type', required=True, domain=[('category_id.is_loan','=',True)])
    state = fields.Selection([('draft','Draft'),('accepted','Accepted'),('refused','Refused'),('done','Done')], 'State', readonly=True, default='draft')
    detail_ids = fields.One2many('hr.loan.detail','loan_id', 'Details')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.loan') or '/'
        return super(hr_loan, self).create(vals)

class hr_loan_detail(models.Model):
    _name= 'hr.loan.detail'
    _order = 'loan_id, state'

    name = fields.Char('Description',size=128)
    loan_id = fields.Many2one('hr.loan',string='Loan', ondelete='cascade')
    start_date = fields.Date('Date')
    base = fields.Float('Base', digits_compute=dp.get_precision('Account'))
    benefit = fields.Float('Benefit', digits_compute=dp.get_precision('Account'))
    total = fields.Float('Total', digits_compute=dp.get_precision('Account'))
    state = fields.Selection([('draft','Draft'),('done','Done')], 'State')
    state_rel = fields.Selection(related='loan_id.state', selection=[('draft', 'Draft'), ('accepted', 'Accepted'), ('refused', 'Refused'), ('done', 'Done')], string="State")

    @api.multi
    def anticipate(self):
        self.state = 'done'
        for loan in self:
            loan_id = loan.loan_id.id
            loan_ids = self.search([('loan_id','=',loan_id),('state','=','draft')])
            if not loan_ids:
                self.env['hr.loan'].write([loan_id], {'state':'done'})
        
        return True

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state == 'done' :
                raise osv.except_osv(_('Warning!'),_('You cannot delete a Loan which is not draft !'))
        return super(hr_loan_detail, self).unlink()

    @api.multi
    def write(self, data):
        for  loan in self:
            if data.get('start_date', loan.start_date) < loan.start_date:
                raise osv.except_osv(_('Warning!'),_('You cannot anticipate a Loan with anterior date !'))
        return super(hr_loan_detail, self).write(data)

class hr_salary_rule_category(models.Model):
    _inherit = 'hr.salary.rule.category'

    is_loan = fields.Boolean('Loan')

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=None):
        res = super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)

        loan_obj = self.pool.get('hr.loan')  
        loan_detail_obj = self.pool.get('hr.loan.detail')  
        contract_obj = self.pool.get('hr.contract')

        for contract in contract_obj.browse(cr, uid, contract_ids, context=context):
            loan_id = loan_obj.search(cr, uid, [('employee_id', '=', contract.employee_id.id),('state', '=', 'accepted')], context=context)
            if loan_id:
                for rule in loan_obj.browse(cr, uid, loan_id, context=context):
                    for loan in rule.detail_ids:
                        if loan.state == 'draft' and loan.start_date<=date_to:
                            inputs = {
                                 'name': rule.rule_id.name,
                                 'code': rule.rule_id.code,
                                 'amount': loan.total,
                                 'contract_id': contract.id,
                            }
                            res += [inputs]
        return res

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'
    
    def close_payslip_run(self, cr, uid, ids, context=None):        
        loan_obj = self.pool.get('hr.loan')
        loan_detail_obj = self.pool.get('hr.loan.detail')
        for payslip in self.browse(cr, uid, ids, context=context).slip_ids:
            date_start = payslip.date_from
            date_end = payslip.date_to
            employee = payslip.employee_id
            loan_id = loan_obj.search(cr, uid, [('employee_id', '=', employee.id), ('state', '=', 'accepted')], context=context)
            loan_ids = loan_detail_obj.search(cr, uid, [('loan_id', '=',loan_id ),('start_date','>',date_start),('start_date','<',date_end)], context=context)
            loan_detail_obj.write(cr, uid, loan_ids, {'state':'done'})
        return super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context=context)

    
    


 
