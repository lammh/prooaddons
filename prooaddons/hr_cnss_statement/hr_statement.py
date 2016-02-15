from openerp import models, fields, api, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp import pooler
import time
from datetime import date, datetime

class hr_cnss(models.Model):
    _name = 'hr.cnss'
    
    @api.multi
    def onchange_cnss(self, company_id, register_id, period, year, codexp):
        result = {'value': {}}
        if not company_id or not register_id or not year or period not in ('1', '2', '3', '4') or not codexp:
            return result
        else:
            result = {'value': { 'detail_ids': [] } }
            line_obj = self.env['hr.cnss.detail']
            nbr = 0
            if int(period) == 1:
                from_date = date(year, 1, 1).strftime('%Y-%m-%d')
                to_date = date(year, 3, 31).strftime('%Y-%m-%d')
            if int(period) == 2:
                nbr = 3
                from_date = date(year, 4, 1).strftime('%Y-%m-%d')
                to_date = date(year, 6, 30).strftime('%Y-%m-%d')
            if int(period) == 3:
                nbr = 6
                from_date = date(year, 7, 1).strftime('%Y-%m-%d')
                to_date = date(year, 9, 30).strftime('%Y-%m-%d')
            if int(period) == 4:
                nbr = 9
                from_date = date(year, 10, 1).strftime('%Y-%m-%d')
                to_date = date(year, 12, 31).strftime('%Y-%m-%d')
            self._cr.execute("select emp.id emp_id, emp.cnss, upper(res.name) as name, \
                identification_id, emp.matricule, sum(total) total \
                from hr_payslip hp \
                inner join hr_payslip_line hl on hp.id = hl.slip_id \
                inner join hr_contract con on con.id = hp.contract_id \
                inner join hr_contract_type ct on ct.id = con.type_id \
                inner join hr_employee emp on emp.id = hp.employee_id \
                inner join resource_resource res on res.id = emp.resource_id \
                where hl.register_id = %s and hp.date_from between %s and %s  \
                and hp.contract_id is not null and ct.exploit_code = %s and res.company_id = %s \
                group by emp.id, emp.cnss, res.name, identification_id, emp.matricule \
                order by emp.matricule", (register_id, from_date , to_date, codexp, company_id))
            payslips = self._cr.dictfetchall()
            if not payslips:
                old_ids = line_obj.search([('cnss_id', '=', self.ids)])
                old_ids.unlink()
            page = ligne = 1
            for slip in payslips:
               if not slip['identification_id']:
                   raise osv.except_osv(_('Error'), _('Missing Identification No for %s') % (slip['name']))
               self._cr.execute("select EXTRACT(MONTH FROM hp.date_from) - %s as rnum, total \
                          from hr_payslip_line hpl inner join hr_payslip hp on hpl.slip_id = hp.id \
                          where hp.employee_id = %s and hp.date_from between %s and %s \
                          and hpl.register_id = %s order by hp.date_from", (nbr, slip['emp_id'], from_date, to_date, register_id))
               all_gross = self._cr.dictfetchall()
               gross1 = gross2 = gross3 = 0.0
               for gross in all_gross:
                   if int(gross['rnum']) == 1: gross1 = gross['total']
                   if int(gross['rnum']) == 2: gross2 = gross['total']
                   if int(gross['rnum']) == 3: gross3 = gross['total']
               if ligne == 13 :
                   page += 1
                   ligne = 1
                   
               rs = {
                    'name': page,
                    'line': ligne,
                    'sec_nbr': slip['cnss'],
                    'emp_name': slip['name'],
                    'matricule': slip['matricule'],
                    'identification_id': slip['identification_id'],
                    'amount': slip['total'],
                    'month1': gross1,
                    'month2': gross2,
                    'month3': gross3,
                }
               result['value']['detail_ids'].append(rs)
               ligne += 1
            return result

    @api.multi
    def unlink (self):
        for cnss in self:
            if cnss.state == 'done':
                raise osv.except_osv(_('Warning!'),_('You cannot delete this Statement !'))
        cnss_ids = self.env['hr.cnss.detail'].search([('cnss_id', '=', self.ids)])
        self.env['hr.cnss.detail'].unlink(cnss_ids)
        return super(hr_cnss, self).unlink()

    @api.multi
    def action_confirm(self):
        self.state = 'done'
        return True

    name = fields.Char('Name', size=64, readonly=True)
    year = fields.Integer('Year', size=4, required=True, default=int(datetime.now().year))
    register_id = fields.Many2one('hr.contribution.register', 'Contribution Register', required=True)
    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env['res.company']._company_default_get('hr.cnss'))
    period = fields.Selection([('1', '1'), ('2', '2'), ('3', '3'), ('4', '4')], 'Period', required=True)
    date = fields.Date('Date', default=date.today())
    codexp = fields.Char('Exploit Code', size=4, required=True, default='00')
    detail_ids = fields.One2many('hr.cnss.detail', 'cnss_id', 'Details')
    note = fields.Text('Note')
    state = fields.Selection([('draft', 'Draft'), ('pending', 'Approved by RH'), ('done', 'Confirmed')], 'State', readonly=True, default='draft')

    _sql_constraints = [
        ('cnss', 'unique(year, period)', 'CNSS Statement must be unique per year and period !'),
    ]

    @api.model
    def create(self, vals):
        company = self.pool.get('res.company').browse(vals['company_id'])
        if not company.company_cnss:
            raise osv.except_osv(_('Error'), _('Missing Employer Number'))
        vals['name'] = "DS" + company.company_cnss + str(vals['codexp'][2:]) + "." + str(vals['period'])[:1] + str(vals['year'])[2:]
        return super(hr_cnss, self).create(vals)

class hr_cnss_detail(models.Model):
    _name = 'hr.cnss.detail'

    cnss_id = fields.Many2one('hr.cnss', 'CNSS Statement',ondelete='cascade' )
    name = fields.Char('Page', size=3)
    line = fields.Char('Line', size=2)
    sec_nbr = fields.Char('Social Security Number', size=12)
    emp_name = fields.Char('Name', size=42)
    matricule = fields.Char('Matricule', size=10)
    identification_id = fields.Char('Identification No', size=8)
    month1 = fields.Float('First Month', digits_compute=dp.get_precision('Account'))
    month2 = fields.Float('Second Month', digits_compute=dp.get_precision('Account'))
    month3 = fields.Float('Third Month', digits_compute=dp.get_precision('Account'))
    amount = fields.Float('Amount', digits_compute=dp.get_precision('Account'))

class hr_employee(models.Model):
    _inherit = 'hr.employee'

    cnss = fields.Char('CNSS No', size=32)

class res_company(models.Model):
    _inherit = "res.company"

    company_cnss = fields.Char('Num CNSS', size=10, required=True, help="The Number consists of 10 character")
