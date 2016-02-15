from openerp import models,fields,api,tools
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
#from dateutil.relativedelta import relativedelta
from datetime import datetime


class OeMedicalPatient(models.Model):
    _name='oemedical.patient'
    _inherits={
        'res.partner': 'partner_id',
    }

    def onchange_name(self, cr, uid, ids, first_name, lastname, slastname, context=None):
        if first_name == False:
            first_name = ''
        if lastname == False:
            lastname = ''
        if slastname == False:
            slastname = ''

        res = {}
        res = {'value': { 
                        'name' : first_name + ' ' + lastname + ' ' + slastname
                         } }
        return res

    # def _get_age(self, cr, uid, ids, field_name, arg, context=None):
    #     res = {}
    #     age = ''
    #     now = datetime.now()
    #     for record in self.browse(cr, uid, ids, context=context):
    #         if (record.dob):
    #             dob = datetime.strptime(str(record.dob), '%Y-%m-%d')
    #
    #             if record.deceased:
    #                 dod = datetime.strptime(record.dod, '%Y-%m-%d %H:%M:%S')
    #                 #delta = relativedelta(dod, dob)
    #                 deceased = ' (deceased)'
    #             else:
    #                 #delta = relativedelta(now, dob)
    #                 deceased = ''
    #             #years_months_days = str(delta.years) + 'y ' \
    #              #       + str(delta.months) + 'm ' \
    #               #      + str(delta.days) + 'd' + deceased
    #         else:
    #             years_months_days = 'No DoB !'
    #
    #         # Return the age in format y m d when the caller is the field name
    #         if field_name == 'age':
    #             age = years_months_days
    #
    #         res[record.id] = age
    #     return res
    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.photo)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'photo': tools.image_resize_image_big(value)})

    @api.one
    @api.depends('photo')
    def _has_photo(self):
        if self.photo:
            self.has_photo = True
        else:
            self.has_photo = False

    @api.one
    @api.depends('dob', 'age')
    def _compute_age(self):
        if self.dob:
            dob = fields.Datetime.from_string(self.dob)
            _logger.warning("Anio nacimiento: %s" % dob)
            today = fields.Datetime.from_string(fields.Datetime.now())
            #_logger.warning("Hoy: %s" % today)
            if today >= dob:
                age = relativedelta(today, dob)
                #_logger.warning(age)
                self.age = age.years
                #_logger.warning("Edad: %s" % self.age)

    @api.one
    @api.depends('partner_id')
    def _get_display_name(self):
         self.display_name = self.partner_id.name

    # @api.multi
    # @api.depends('first_name', 'lastname')
    # def name_get(self):
    #     result = []
    #     for record in self:
    #         result.append((record.id,record.name))
    #     return result


    display_name = fields.Char(compute ='_get_display_name')
    partner_id = fields.Many2one(
        'res.partner', 'Related Partner', required=True,
        ondelete='cascade', help='Partner-related data of the patient')
    first_name = fields.Char(size=256, string='Name', required=True)
    lastname = fields.Char(size=256, string='Lastname', required=True)
    slastname = fields.Char(size=256, string='Second Lastname',)
    family = fields.Many2one('oemedical.family', string='Family', help='Family Code')
    photo = fields.Binary(string='Picture')
    has_photo = fields.Boolean(compute='_has_photo',store=True)
    sex = fields.Selection([('m', 'Male'), ('f', 'Female'), ], string='Sex', required=True)
    blood_type = fields.Selection([
                                    ('A', 'A'),
                                    ('B', 'B'),
                                    ('AB', 'AB'),
                                    ('O', 'O'), ], string='Blood Type')
    rh = fields.Selection([
                                    ('+', '+'),
                                    ('-', '-'), ], string='Rh')
    general_info = fields.Text(string='General Information', help='General information about the patient')
    primary_care_doctor = fields.Many2one('oemedical.physician', 'Primary Care Doctor', help='Current primary care / family doctor')
    childbearing_age = fields.Boolean('Potential for Childbearing')
    medications = fields.One2many('oemedical.patient.medication', 'patient_id', string='Medications',)
    evaluations = fields.One2many('oemedical.patient.evaluation', 'patient_id', string='Evaluations',)
    critical_info = fields.Text( string='Important disease, allergy or procedures information', help='Write any important information on the patient\'s disease, surgeries, allergies, ...')
    diseases = fields.One2many('oemedical.patient.disease', 'patient_id', string='Diseases', help='Mark if the patient has died')
    ethnic_group = fields.Many2one('oemedical.ethnicity', string='Ethnic group',)
    ssn = fields.Char(size=256, string='SSN',)
    vaccinations = fields.One2many('oemedical.vaccination', 'patient_id', 'Vaccinations',)
    dob = fields.Date(string='DoB')
    age = fields.Char(compute ='_compute_age', string='Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field", multi=False)
    marital_status = fields.Selection([('s', 'Single'), ('m', 'Married'),
                                        ('w', 'Widowed'),
                                        ('d', 'Divorced'),
                                        ('x', 'Separated'),
                                        ('z', 'law marriage'),
                                        ],
                                       string='Marital Status', sort=False)
    dod = fields.Datetime(string='Date of Death')
    current_insurance = fields.Many2one('oemedical.insurance', string='Insurance', help='Insurance information. You may choose from the different insurances belonging to the patient')
    cod = fields.Many2one('oemedical.pathology', string='Cause of Death',)
    identification_code = fields.Char(size=256, string='ID', help='Patient Identifier provided by the Health Center.Is not the Social Security Number')
    deceased = fields.Boolean(string='Deceased')

    _defaults={
         'ref': lambda obj, cr, uid, context: 
                obj.pool.get('ir.sequence').get(cr, uid, 'oemedical.patient'),
                 }

    def create(self, cr, uid, vals, context=None):
       # sequence = unicode (self.pool.get('ir.sequence').get(cr, uid, 'oemedical.patient'))
        #vals['identification_code'] = sequence
        return super(OeMedicalPatient, self).create(cr, uid, vals, context=context)
    
