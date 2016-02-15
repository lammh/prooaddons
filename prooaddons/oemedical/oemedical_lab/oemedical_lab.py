
import time
#from mx import DateTime
import datetime
from openerp import models,fields,_
#from tools.translate import _
# Add Lab test information to the Patient object

class oemedical_patient (models.Model):
    _name = "oemedical.patient"
    _inherit = "oemedical.patient"

    # def name_get(self, cr, uid, ids, context={}):
    #     if not len(ids):
    #         return []
    #     rec_name = 'name'
    #     res = [(r['id'], r[rec_name][1]) for r in self.read(cr, uid, ids, [rec_name], context)]
    #     return res

    # def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
    #     if not args:
    #         args=[]
    #     if not context:
    #         context={}
    #     if name:
    #         ids = self.search(cr, user, [('patient_id','=',name)]+ args, limit=limit, context=context)
    #         if not len(ids):
    #             ids += self.search(cr, user, [('name',operator,name)]+ args, limit=limit, context=context)
    #     else:
    #         ids = self.search(cr, user, args, limit=limit, context=context)
    #     result = self.name_get(cr, user, ids, context)
    #     return result

    lab_test_ids = fields.One2many('oemedical.patient.lab.test','patient_id','Lab Tests Required')


    
class test_type (models.Model):
    _name = "oemedical.test_type"
    _description = "Type of Lab test"

    name = fields.Char ('Test',size=128,help="Test type, eg X-Ray, hemogram,biopsy...")
    code = fields.Char ('Code',size=128,help="Short name - code for the test")
    info = fields.Text ('Description')
    product_id = fields.Many2one('product.product', 'Service', required=True)
    critearea = fields.One2many('oemedical_test.critearea','test_type_id','Test Cases')


    _sql_constraints = [
            ('code_uniq', 'unique (name)', 'The Lab Test code must be unique')]


class lab (models.Model):
    _name = "oemedical.lab"
    _description = "Lab Test"

    name = fields.Char ('ID', size=128, help="Lab result ID")
    test = fields.Many2one ('oemedical.test_type', 'Test type', help="Lab test type")
    patient = fields.Many2one ('oemedical.patient', 'Patient', help="Patient ID")
    pathologist = fields.Many2one ('oemedical.physician','Pathologist',help="Pathologist")
    requestor = fields.Many2one ('oemedical.physician', 'Physician', help="Doctor who requested the test")
    results = fields.Text ('Results')
    diagnosis = fields.Text ('Diagnosis')
    critearea = fields.One2many('oemedical_test.critearea','oemedical_lab_id','Test Cases')
    date_requested = fields.Datetime ('Date requested')
    date_analysis = fields.Datetime ('Date of the Analysis')

    _defaults = {
        'date_requested': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_analysis': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name' : lambda obj, cr, uid, context: obj.pool.get('ir.sequence').get(cr, uid, 'oemedical.lab'),
         }


    _sql_constraints = [
        ('id_uniq', 'unique (name)', 'The test ID code must be unique')]




class oemedical_lab_test_units(models.Model):
    _name = "oemedical.lab.test.units"

    name = fields.Char('Unit', size=25)
    code = fields.Char('Code', size=25)

    _sql_constraints = [
            ('name_uniq', 'unique(name)', 'The Unit name must be unique')]
    


class oemedical_test_critearea(models.Model):
    _name = "oemedical_test.critearea"
    _description = "Lab Test Critearea"

    name = fields.Char('Test', size=64)
    result = fields.Text('Result')
    normal_range = fields.Text('Normal Range')
    units = fields.Many2one('oemedical.lab.test.units', 'Units')
    test_type_id = fields.Many2one('oemedical.test_type','Test type')
    oemedical_lab_id = fields.Many2one('oemedical.lab','Test Cases')
    sequence = fields.Integer('Sequence')

    _defaults = {
        'sequence' : lambda *a : 1,
         }
    _order="sequence"


    

class oemedical_patient_lab_test(models.Model):
    _name = 'oemedical.patient.lab.test'
    def _get_default_dr(self, cr, uid, context={}):
        partner_id = self.pool.get('res.partner').search(cr,uid,[('user_id','=',uid)])
        if partner_id:
            dr_id = self.pool.get('oemedical.physician').search(cr,uid,[('name','=',partner_id[0])])
            if dr_id:
                return dr_id[0]
            #else:
            #    raise osv.except_osv(_('Error !'),
            #            _('There is no physician defined ' \
            #                    'for current user.'))
        else:
            return False
        

    name = fields.Many2one('oemedical.test_type','Test Type')
    date = fields.Datetime('Date')
    state = fields.Selection([('draft','Draft'),('tested','Tested'),('cancel','Cancel')],'State',readonly=True)
    patient_id = fields.Many2one('oemedical.patient','Patient')
    doctor_id = fields.Many2one('oemedical.physician','Doctor', help="Doctor who Request the lab test.")
    #'invoice_status' : fields.selection([('invoiced','Invoiced'),('tobe','To be Invoiced'),('no','No Invoice')],'Invoice Status'),

    _defaults={
       'date' : lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
       'state' : lambda *a : 'draft',
       'doctor_id' : _get_default_dr,        
	   #'invoice_status': lambda *a: 'tobe',
       }
    



