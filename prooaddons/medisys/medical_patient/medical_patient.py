from openerp import models,fields,api,tools
from openerp.osv import osv
from dateutil.relativedelta import relativedelta
import logging
_logger = logging.getLogger(__name__)
from datetime import datetime


class MediSysPatient(models.Model):
    _name='medical.patient'
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
            today = fields.Datetime.from_string(fields.Datetime.now())
            if today >= dob:
                age = relativedelta(today, dob)
                self.age = age.years

    def _compute_duration(self):
        if self.doe:
            doe = fields.Datetime.from_string(self.doe)
            today = fields.Datetime.from_string(fields.Datetime.now())
            duration = relativedelta(today, doe)
            self.duration_stay = duration

    def _compute_duration_rea(self):
        if self.doer:
            doer = fields.Datetime.from_string(self.doer)
            today = fields.Datetime.from_string(fields.Datetime.now())
            duration = relativedelta(today, doer)
            self.duration_stay = duration

    @api.one
    @api.depends('partner_id')
    def _get_display_name(self):
         self.display_name = self.partner_id.name

    ############ Columns ############
    display_name = fields.Char(compute ='_get_display_name')
    first_name = fields.Char(size=256, string='Name', required=True)
    lastname = fields.Char(size=256, string='Lastname', required=True)
    slastname = fields.Char(size=256, string='Second Lastname',) 
    partner_id = fields.Many2one('res.partner', 'Related Partner', required=True,
        ondelete='cascade', help='Partner-related data of the patient')
    identification_code = fields.Char(size=256, string='ID')
    admission_pattern = fields.Many2one('medical.service', string='Admission pattern')
    admission_type = fields.Many2one('medical.type', String='Admission Type')
    room = fields.Many2one('medical.room', 'Room', domain=[('state', '=', 'ready')])
    categ_room = fields.Many2one('product.product', 'Category', domain="[('is_categ_room', '=', True)]", required=True)
    doe = fields.Datetime(string='Date Of Entry')
    dor = fields.Datetime(string='Date Of Release')
    duration_stay = fields.Char(compute ='_compute_duration', string='Duration Stay', multi=False)
    doer = fields.Datetime(string='Date Of Entry into Reanimation')
    duration_stay_rea = fields.Char(compute ='_compute_duration_rea', string='Duration Stay Reanimation', multi=False)
    dorr = fields.Datetime(string='Date Of Release Reanimation')
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
    attending_doctor = fields.Many2one('medical.doctor', 'Attending Doctor')
    critical_info = fields.Text( string='Important disease, allergy or procedures information', help='Write any important information on the patient\'s disease, surgeries, allergies, ...')
    ssn = fields.Char(size=256, string='SSN',)
    dob = fields.Date(string='Date of Birth')
    pob = fields.Char(size=256, string='Place of Birth')
    age = fields.Char(compute ='_compute_age', string='Age', help="It shows the age of the patient in years(y), months(m) and days(d).\nIf the patient has died, the age shown is the age at time of death, the age corresponding to the date on the death certificate. It will show also \"deceased\" on the field", multi=False)
    weight = fields.Float('Weight')
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

    deceased = fields.Boolean(string='Deceased')
    state = fields.Selection([('pre', 'Pre-admitted'), 
                              ('hospitalized', 'Hospitalized'), 
                              ('not', 'not hospitalized'), 
                              ('cancel', 'Cancel')], 'State', readonly=True)
    invoice_id = fields.Many2one('account.invoice', 'Invoice')

    _defaults={
                 }

    def onchange_room(self, cr, uid, ids, room, context=None):
        r = {'value': {}}
        if not room:
            return r
        r['value']['categ_room'] = self.pool.get('medical.room').browse(cr, uid, room, context=context).categ_id.id
        return r

    def invoice_line(self, cr, uid, invoice_id, categ_room_id, context=None):
        invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id, context=context)
        categ_room = self.pool.get('product.product').browse(cr, uid, categ_room_id, context=context)
        account_id = categ_room.property_account_income.id
        if not account_id:
            account_id = categ_room.categ_id.property_account_income_categ.id
            if not account_id:
                raise osv.except_osv(_('Error!'),
                    _('Please define income account for this product: "%s" (id:%d).') % \
                        (categ_room.name, categ_room.id,))
        res = {
            'name': categ_room.name_template,
            'sequence': 1,
            'origin': '',
            'account_id': account_id,
            'price_unit': categ_room.list_price,
            'quantity': 1.0,
            'uos_id': categ_room.uos_id.id,
            'product_id': categ_room_id,
            'invoice_line_tax_id': [(6, 0, [x.id for x in categ_room.taxes_id])],
            'invoice_id': invoice_id,
            'company_id': invoice.partner_id.company_id.id,
            'discount': 0,
            }
        self.pool.get('account.invoice.line').create(cr, uid, res, context=context)
        return True

    def create(self, cr, uid, vals, context=None):
        if vals['room']:
            room = self.pool.get('medical.room').browse(cr, uid, vals['room'], context=context)
            if room.state != 'ready':
                raise osv.except_osv(_("Warning !"), _("Room not Ready"))
        room.write({'state':'occupied'})
        sequence = unicode (self.pool.get('ir.sequence').get(cr, uid, 'medisys.patient'))
        vals['identification_code'] = sequence
        vals['doe'] = fields.Datetime.now()
        res = super(MediSysPatient, self).create(cr, uid, vals, context=context)
        patient = self.browse(cr, uid, res, context=context)
        vals['invoice_id'] = self.pool.get('account.invoice').create(cr, uid, 
                             {'partner_id': patient.partner_id.id, 
                              'account_id': patient.partner_id.property_account_receivable.id}, context=context)
        self.invoice_line(cr, uid, vals['invoice_id'], vals['categ_room'], context=context)
        return res

    def run_scheduler(self, cr, uid, automatic=False, use_new_cursor=False, context=None):
        patient_obj = self.pool.get('medical.patient')
        patient_ids = patient_obj.search(cr, uid, [('state', '=', 'hospitalized')])
        for patient in patient_obj.browse(cr, uid, patient_ids):
            self.invoice_line(cr, uid, patient.invoice_id.id, patient.categ_room.id, context=context)
    
