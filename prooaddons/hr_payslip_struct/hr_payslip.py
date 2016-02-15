from openerp import models, fields, api, _
from openerp.osv import osv
import datetime, time
from datetime import date, timedelta
import openerp.addons.decimal_precision as dp


class hr_holiday(models.Model):
    _inherit = 'hr.holidays'

    appears_on_payslip = fields.Boolean('Appears on Payslip', default=True)

class hr_payslip_input(models.Model):
    _inherit = 'hr.payslip.input'

    amount = fields.Float('Amount', digits_compute=dp.get_precision('Payroll'), help="It is used in computation. For e.g. A rule for sales having 1% commission of basic salary for per product can defined in expression like result = inputs.SALEURO.amount * contract.wage*0.01.")

class hr_payslip_run(models.Model):
    _inherit = 'hr.payslip.run'

    struct_id = fields.Many2one('hr.payroll.structure', 'Salary Structure')

    def draft_payslip_run(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        for payslip in self.browse(cr, uid, ids, context=context).slip_ids:
            payslip_obj.write(cr, uid, payslip.id, {'state':'draft'})
        super(hr_payslip_run, self).draft_payslip_run(cr, uid, ids, context=context)

    def close_payslip_run(self, cr, uid, ids, context=None):
        payslip_obj = self.pool.get('hr.payslip')
        for payslip in self.browse(cr, uid, ids, context=context).slip_ids:
            payslip_obj.write(cr, uid, payslip.id, {'state':'done'})
        return super(hr_payslip_run, self).close_payslip_run(cr, uid, ids, context=context)

class hr_payslip_employees(models.TransientModel):
    _inherit ='hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        struct_pool = self.pool.get('hr.payroll.structure')

        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, context['active_id'], ['date_start', 'date_end', 'credit_note','struct_id'])
        from_date =  run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        struct_id = run_data.get('struct_id', False)
        credit_note = run_data.get('credit_note', False)
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date,context.get('active_id', False), emp.id, contract_id=False , context=context)
            res = {                
                'employee_id': emp.id,
                'date_from': from_date,
                'date_to': to_date,
                'name': slip_data['value'].get('name', False),
                'struct_id': struct_id[0],
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'credit_note': credit_note,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

class hr_payslip(models.Model):
    _inherit = 'hr.payslip'

    @api.one
    def compute_months(self):
        res = {}
        for record in self:
            month = str((date(*time.strptime(str(record.date_from),'%Y-%m-%d')[:3])).strftime('%m'))
            remaining_months = 12 - int(month)
            self.nbr_months = remaining_months

    employee_name = fields.Char(related='employee_id.name', string='Employee', store=True)
    employee_department = fields.Many2one(related='employee_id.department_id', relation='hr.department', string='Department', store=True)
    employee_job = fields.Many2one(related='employee_id.job_id', relation='hr.job', string='Job', store=True)
    employee_children = fields.Integer(related='employee_id.children', string='Children', store=True)
    nbr_months = fields.Integer(compute='compute_months', string='Number of months', readonly=True)
    
    def get_inputs(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id=False, context=None):
        return super(hr_payslip, self).get_inputs(cr, uid, contract_ids, date_from, date_to, context=context)
    
    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, payslip_run_id=False, context=None):
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day), ('appears_on_payslip','=',True)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            total = {
                 'name': _("Normal Working Days"),
                 'sequence': 1,
                 'code': 'TOTAL',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            leaves = {}
            day_from = datetime.datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.datetime.strptime(date_to,"%Y-%m-%d")
            if contract.date_end and str(day_to) > contract.date_end:
                day_to = datetime.datetime.strptime(contract.date_end,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }
                    else:
                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day
                    total['number_of_days'] += 1.0
                    total['number_of_hours'] += working_hours_on_day
            leaves = [value for key,value in leaves.items()]
            res += [total] + [attendances] + leaves
        return res

    def onchange_struct_id(self, cr, uid, ids, payslip_run_id, employee_id, context=None):
        if not payslip_run_id or not employee_id:
            return {}
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        payslip_run = self.pool.get('hr.payslip.run').browse(cr, uid, payslip_run_id)
        res = {'value': {
            'name': '',
            'company_id': '',
                        }
               }
        res['value'].update({
                        'name': _('Salary Slip of %s for %s') % (employee.name, payslip_run.name),
                        'company_id': employee.company_id.id
            })
        return res

    def onchange_employee_id(self, cr, uid, ids, date_from, date_to, payslip_run_id=False, employee_id=False, contract_id=False, context=None):
        empolyee_obj = self.pool.get('hr.employee')
        contract_obj = self.pool.get('hr.contract')
        worked_days_obj = self.pool.get('hr.payslip.worked_days')
        input_obj = self.pool.get('hr.payslip.input')
        run_obj = self.pool.get('hr.payslip.run')
        if context is None:
            context = {}
        #delete old worked days lines
        old_worked_days_ids = ids and worked_days_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_worked_days_ids:
            worked_days_obj.unlink(cr, uid, old_worked_days_ids, context=context)

        #delete old input lines
        old_input_ids = ids and input_obj.search(cr, uid, [('payslip_id', '=', ids[0])], context=context) or False
        if old_input_ids:
            input_obj.unlink(cr, uid, old_input_ids, context=context)


        #defaults
        res = {'value':{
                      'line_ids':[],
                      'input_line_ids': [],
                      'worked_days_line_ids': [],
                      #'details_by_salary_head':[], TODO put me back
                      'name':'',
                      'contract_id': False,
                      'struct_id': False,
                      }
            }
        if (not employee_id) or (not date_from) or (not date_to):
            return res
        payslip_run = run_obj.browse(cr, uid, payslip_run_id, context=context)
        employee_id = empolyee_obj.browse(cr, uid, employee_id, context=context)
        res['value'].update({
                        'name': _('Salary Slip of %s for %s') % (employee_id.name, payslip_run and payslip_run.name or '' ),
                        'company_id': employee_id.company_id.id
            })

        if not context.get('contract', False):
            #fill with the first contract of the employee
            contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)
        else:
            if contract_id:
                #set the list of contract for which the input have to be filled
                contract_ids = [contract_id]
            else:
                #if we don't give the contract, then the input to fill should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, employee_id, date_from, date_to, context=context)

        if not contract_ids:
            return res
        contract_record = contract_obj.browse(cr, uid, contract_ids[0], context=context)
        res['value'].update({
                    'contract_id': contract_record and contract_record.id or False
        })
        #computation of the salary input
        worked_days_line_ids = self.get_worked_day_lines(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)
        input_line_ids = self.get_inputs(cr, uid, contract_ids, date_from, date_to, payslip_run_id, context=context)
        res['value'].update({
                    'worked_days_line_ids': worked_days_line_ids,
                    'input_line_ids': input_line_ids,
        })
        return res


