from openerp import models, fields
import openerp.addons.decimal_precision as dp
import time
from datetime import date
from dateutil import relativedelta
from openerp.tools.translate import _
 
class hr_holidays_status(models.Model):
    _inherit = "hr.holidays.status"

    paid_leave = fields.Boolean('Paid Leave')
    
    _sql_constraints = [
        ('paid_leave', 'unique(name, paid_leave)', 'Holidays paid leave must be unique !'),
    ]

class hr_employee(models.Model):
    _inherit="hr.employee"

    remaining_paid_leaves = fields.Float('Remaining Paid Leaves', digits_compute=dp.get_precision('Account'), required=True)
            
class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'
     
    def close_payslip_run(self, cr, uid, ids, context=None):
         res = {}
         holiday_obj = self.pool.get('hr.holidays')
         holiday_id = self.pool.get('hr.holidays.status').search(cr, uid, [('paid_leave','=',True)])
         emp_ids = self.pool.get('hr.payslip').search(cr, uid, [('payslip_run_id','=',ids)])
         for payslip in self.pool.get('hr.payslip').browse(cr, uid, emp_ids, context=context):
             inputs = {
                      'name': _('Right to leave ' + str((date(*time.strptime(str(payslip.date_from),'%Y-%m-%d')[:3])).strftime('%Y-%m'))),
                      'holiday_type': 'employee',
                      'holiday_status_id': holiday_id[0],
                      'employee_id': payslip.employee_id.id,
                      'number_of_days_temp': payslip.employee_id.remaining_paid_leaves,
                      'state':'validate',
                      'type':'add',
                  }
             holiday_obj.create(cr, uid, inputs, context=context)
         return super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context=context)