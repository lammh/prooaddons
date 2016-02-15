from openerp import models,fields,api


class MedicalService(models.Model):
    _name = 'medical.service'
    _inherits={
        'stock.location': 'location_id',
    }
    location_id = fields.Many2one('stock.location', string='Location', required=True)
    sequence_id = fields.Many2one('ir.sequence', 'Entry Sequence'),

    _defaults={
            'usage': 'view',
            'sequence_id': lambda s,cr,uid,c: s.pool.get('ir.sequence').search(cr, uid, [('code', '=', 'medisys.patient')])[0],
                 }

    def create_sequence(self, cr, uid, vals, context=None):
        prefix = vals['name'].upper()[:1]

        seq = {
            'name': vals['name'],
            'implementation':'no_gap',
            'prefix': prefix + "/%(y)s/",
            'padding': 5,
            'number_increment': 1
        }
        if 'company_id' in vals:
            seq['company_id'] = vals['company_id']
        return self.pool.get('ir.sequence').create(cr, uid, seq)

    def create(self, cr, uid, vals, context=None):
        if not 'sequence_id' in vals or not vals['sequence_id']:
            vals.update({'sequence_id': self.create_sequence(cr, SUPERUSER_ID, vals, context)})
        return super(MedicalService, self).create(cr, uid, vals, context)
