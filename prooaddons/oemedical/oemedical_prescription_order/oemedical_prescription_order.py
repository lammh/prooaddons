from openerp import models,fields
from openerp import netsvc
from datetime import datetime, timedelta
#from dateutil.relativedelta import relativedelta
import time



class OeMedicalPrescriptionOrder(models.Model):
    _name='oemedical.prescription.order'


    patient_id = fields.Many2one('oemedical.patient', string='Patient', required=True)
    pregnancy_warning = fields.Boolean(string='Pregancy Warning', readonly=True)
    notes = fields.Text(string='Prescription Notes')
    prescription_line = fields.One2many('oemedical.prescription.line', 'name', string='Prescription line',)
    pharmacy = fields.Many2one('res.partner', string='Pharmacy',)
    prescription_date = fields.Datetime(string='Prescription Date')
    prescription_warning_ack = fields.Boolean( string='Prescription verified')
    physician_id = fields.Many2one('oemedical.physician', string='Prescribing Doctor',  required=True)
    name = fields.Char(size=256, string='Prescription ID', required=True, help='Type in the ID of this prescription')

    
    _defaults={
         'name': lambda obj, cr, uid, context: 
            obj.pool.get('ir.sequence').get(cr, uid,
                                            'oemedical.prescription.order'),
	    'prescription_date':lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),

                 }

    def print_prescription(self, cr, uid, ids, context=None):
        '''
        '''
#        assert len(ids) == 1, 'This option should only be used for a single id at a time'
#        wf_service = netsvc.LocalService("workflow")
#        wf_service.trg_validate(uid, 'oemedical.prescription.order', ids[0], 'prescription_sent', cr)
        datas = {
                 'model': 'oemedical.prescription.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'prescription.order', 'datas': datas, 'nodestroy': True}


