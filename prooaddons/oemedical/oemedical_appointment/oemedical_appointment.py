
from openerp import models,fields
import time


class OeMedicalAppointment(models.Model):
    _name = 'oemedical.appointment'

    patient_id = fields.Many2one('oemedical.patient', string='Patient',
                               required=True, select=True,
                               help='Patient Name')
    name = fields.Char(size=256, string='Appointment ID', readonly=True)
    appointment_date = fields.Datetime(string='Date and Time')
    appointment_day = fields.Date(string='Date')
    appointment_hour = fields.Selection([
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
         ],
        string='Hour')
    appointment_minute = fields.Selection([
        ('05', '05'),
        ('10', '10'),
        ('15', '15'),
        ('20', '20'),
        ('25', '25'),
        ('30', '30'),
        ('35', '35'),
        ('40', '40'),
        ('45', '45'),
        ('50', '50'),
        ('55', '55'),
         ],
        string='Minute')

    duration = fields.Float('Duration')
    doctor = fields.Many2one('oemedical.physician',
                              string='Physician',select=True,
                              help='Physician\'s Name')
    alias = fields.Char(size=256, string='Alias', )
    comments = fields.Text(string='Comments')
    appointment_type = fields.Selection([
        ('ambulatory', 'Ambulatory'),
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
    ], string='Type')
    institution = fields.Many2one('res.partner',
                                   string='Health Center',
                                   help='Medical Center'
                                    , domain="[('category_id', '=', 'Doctor Office')]")
    consultations = fields.Many2one('product.product',
                                     string='Consultation Services',
                                      help='Consultation Services'
                                    , domain="[('type', '=', 'service'), ]")
    urgency = fields.Selection([
        ('a', 'Normal'),
        ('b', 'Urgent'),
        ('c', 'Medical Emergency'), ],
        string='Urgency Level')
    speciality = fields.Many2one('oemedical.specialty',
                                  string='Specialty',
                                  help='Medical Specialty / Sector')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'Confirm'),
        ('waiting', 'Wating'),
        ('in_consultation', 'In consultation'),
        ('done', 'Done'),
        ('canceled', 'Canceled'),
         ],
        string='State')
    history_ids = fields.One2many('oemedical.appointment.history','appointment_id_history','History lines', states={'start':[('readonly',True)]})


    _defaults = {
        'name': lambda obj, cr, uid, context: 
            obj.pool.get('ir.sequence').get(cr, uid, 'oemedical.appointment'),
        'duration': 30.00,
        'urgency': 'a',
        'state': 'draft',

                 }

    def create(self, cr, uid, vals, context=None):
        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')



        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to Comfirm  ------------------------------------\n"

        vals['history_ids'] = val_history

        #print "create", vals['history_ids'], val_history, '     ------    ', vals

        return super(OeMedicalAppointment, self).create(cr, uid, vals, context=context)

    def button_back(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        for order in self.browse(cr, uid, ids, context=context):
            if order.state == 'confirm':
                self.write(cr, uid, ids, {'state':'draft'} ,context=context)
                val_history['action'] = "--------------------------------  Changed to Draft  ------------------------------------\n"
            if order.state == 'waiting':
                val_history['action'] = "--------------------------------  Changed to Confirm  ------------------------------------\n"
                self.write(cr, uid, ids, {'state':'confirm'} ,context=context)
            if order.state == 'in_consultation':
                val_history['action'] = "--------------------------------  Changed to Waiting  ------------------------------------\n"
                self.write(cr, uid, ids, {'state':'waiting'} ,context=context)
            if order.state == 'done':
                val_history['action'] = "--------------------------------  Changed to In Consultation  ------------------------------------\n"
                self.write(cr, uid, ids, {'state':'in_consultation'} ,context=context)
            if order.state == 'canceled':
                val_history['action'] = "--------------------------------  Changed to Draft  ------------------------------------\n"
                self.write(cr, uid, ids, {'state':'draft'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')

        ait_obj.create(cr, uid, val_history)

        return True

    def button_confirm(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        self.write(cr, uid, ids, {'state':'confirm'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to Comfirm  ------------------------------------\n"
        ait_obj.create(cr, uid, val_history)

        return True

    def button_waiting(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        self.write(cr, uid, ids, {'state':'waiting'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to Waiting  ------------------------------------\n"
        ait_obj.create(cr, uid, val_history)

        return True

    def button_in_consultation(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        self.write(cr, uid, ids, {'state':'in_consultation'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to In Consultation  ------------------------------------\n"
        ait_obj.create(cr, uid, val_history)

        return True

    def button_done(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        self.write(cr, uid, ids, {'state':'done'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to Done  ------------------------------------\n"
        ait_obj.create(cr, uid, val_history)

        return True

    def button_cancel(self, cr, uid, ids, context=None):

        val_history = {}
        ait_obj = self.pool.get('oemedical.appointment.history')

        self.write(cr, uid, ids, {'state':'canceled'} ,context=context)

        val_history['appointment_id_history'] = ids[0]
        val_history['name'] = uid
        val_history['date'] = time.strftime('%Y-%m-%d %H:%M:%S')
        val_history['action'] = "--------------------------------  Changed to Canceled  ------------------------------------\n"
        ait_obj.create(cr, uid, val_history)

        return True


class OeMedicalAppointment_history(models.Model):
    _name = 'oemedical.appointment.history'

    appointment_id_history =  fields.Many2one('oemedical.appointment','History', ondelete='cascade')
    date = fields.Datetime(string='Date and Time')
    name = fields.Many2one('res.users', string='User', help='')
    action = fields.Text('Action')

    _defaults = {
                 }

