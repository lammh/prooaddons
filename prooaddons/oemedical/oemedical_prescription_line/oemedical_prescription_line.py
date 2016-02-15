from openerp import models,fields


class OeMedicalPrescriptionLine(models.Model):
    _name = 'oemedical.prescription.line'



    def _get_medicament(self, cr, uid, ids, name, args, context=None):
        #print '_get_medicament', name, args, context, ids
        medication_obj = self.pool.get('oemedical.medication.template')
        result = {}

#        if name == 'form':
#            result = {'value': { 
#                        'form' : medication_obj.browse(cr, uid, medication, context = None).form.id ,
#                         } }
        return result

#    def _get_dose(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for record in self.browse(cr, uid, ids, context=context):
#            res[record.id] = record.template.dose
#        return res

#    def _get_frecuency(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for record in self.browse(cr, uid, ids, context=context):
#            res[record.id] = 1
#        return res


#    def _get_duration(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for record in self.browse(cr, uid, ids, context=context):
#            res[record.id] = 1
#        return res

#    def _get_qty(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for record in self.browse(cr, uid, ids, context=context):
#            res[record.id] = 1
#        return res

#    def _get_frecuency_unit(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        return res

#    def _get_admin_times(self, cr, uid, ids, name, args, context=None):
#        res = {}
#        return res

#    def _get_start_treatment(self, cr, uid, ids, field_name, arg, context=None):
#        ops = self.browse(cr, uid, ids, context=context)
#        res = {}
#        for op in ops:
#            res[op.id] = False
#        return res

#    def _get_end_treatment(self, cr, uid, ids, field_name, arg, context=None):
#        ops = self.browse(cr, uid, ids, context=context)
#        res = {}
#        for op in ops:
#            res[op.id] = False
#        return res

#    def _get_duration_period(self, cr, uid, ids, field_name, arg, context=None):
#        res = {}
#        for line in self.browse(cr, uid, ids, context=context):
#            res[line.id] = 'days'
#        return res

    def onchange_template(self, cr, uid, ids, medication, context=None):
        medication_obj = self.pool.get('oemedical.medication.template')
        res = {}
        res = {'value': { 
                        'indication' : medication_obj.browse(cr, uid, medication, context = None).indication.id ,
                        'form' : medication_obj.browse(cr, uid, medication, context = None).form.id ,
                        'route' : medication_obj.browse(cr, uid, medication, context = None).route.id ,
                        'dose' : medication_obj.browse(cr, uid, medication, context = None).dose ,
                        'dose_unit' : medication_obj.browse(cr, uid, medication, context = None).dose_unit.id ,
                        'qty' : medication_obj.browse(cr, uid, medication, context = None).qty ,
                        'admin_times' : medication_obj.browse(cr, uid, medication, context = None).admin_times ,
                        'common_dosage' : medication_obj.browse(cr, uid, medication, context = None).common_dosage.id ,
                        'frequency' : medication_obj.browse(cr, uid, medication, context = None).frequency ,
                        'frequency_unit' : medication_obj.browse(cr, uid, medication, context = None).frequency_unit ,
                         } }
        return res


    name = fields.Many2one('oemedical.prescription.order', string='Prescription ID', )
    template = fields.Many2one('oemedical.medication.template', string='Medication', )
    indication = fields.Many2one('oemedical.pathology', string='Indication', help='Choose a disease for this medicament from the disease list. It'\
                    ' can be an existing disease of the patient or a prophylactic.')
    allow_substitution = fields.Boolean(string='Allow substitution')
    prnt = fields.Boolean(string='Print', help='Check this box to print this line of the prescription.')
    quantity = fields.Integer(string='Units',  help="Number of units of the medicament. Example : 30 capsules of amoxicillin")
    active_component = fields.Char(size=256, string='Active component', help='Active Component')
    start_treatment = fields.Datetime(string='Start')
    end_treatment = fields.Datetime(string='End')
    dose = fields.Float('Dose', digits=(16, 2), help="Amount of medication (eg, 250 mg) per dose")
    dose_unit = fields.Many2one('product.uom', string='Dose Unit', help='Amount of medication (eg, 250 mg) per dose')
    qty = fields.Integer('x')
    form = fields.Many2one('oemedical.drug.form', string='Form', help='Drug form, such as tablet or gel')
    route = fields.Many2one('oemedical.drug.route', string='Route', help='Drug form, such as tablet or gel')
    common_dosage = fields.Many2one('oemedical.medication.dosage', string='Frequency', help='Drug form, such as tablet or gel')
    admin_times = fields.Char('Admin Hours', size=255)
    frequency = fields.Integer('Frequency')
    frequency_unit = fields.Selection([
                            (None, ''),
                            ('seconds', 'seconds'),
                            ('minutes', 'minutes'),
                            ('hours', 'hours'),
                            ('days', 'days'),
                            ('weeks', 'weeks'),
                            ('wr', 'when required'),
                                ],'Unit')
    frequency_prn = fields.Boolean(string='Frequency prn', help='')
    duration = fields.Integer('Treatment duration')
    duration_period = fields.Selection([
                            (None, ''),
                            ('minutes', 'minutes'),
                            ('hours', 'hours'),
                            ('days', 'days'),
                            ('months', 'months'),
                            ('years', 'years'),
                            ('indefinite', 'indefinite'),
                                ],'Treatment period')
    refills = fields.Integer(string='Refills #')
    review = fields.Datetime(string='Review')
    short_comment = fields.Char(size=256, string='Comment', help='Short comment on the specific drug')


    _defaults = {
        'prnt' : True,

                }

