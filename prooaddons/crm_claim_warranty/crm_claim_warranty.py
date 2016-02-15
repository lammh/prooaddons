from openerp import models, fields, api
from dateutil.relativedelta import relativedelta
from datetime import datetime

class crm_claim(models.Model):
    _inherit = "crm.claim"

    date_start_warranty = fields.Date('Warranty start date')
    date_end_warranty = fields.Date('Warranty end date')
    warranty = fields.Char('Warranty')

    @api.multi
    def onchange_warranty(self, ref, date_start_warranty, date):
        if not ref or not date_start_warranty:
            return {}
        if ref.split(',')[0] != 'stock.production.lot':
            return {}
        model = ref.split(',')[0]
        id = ref.split(',')[1]
        lot = self.env[model].browse(int(id))
        for l in lot:
            date_end = datetime.strptime(date_start_warranty, '%Y-%m-%d') + relativedelta(months=int(l.product_id.warranty), days=-1)
        warranty = ''
        if datetime.strptime(date, '%Y-%m-%d %H:%M:%S') > date_end:
            warranty = 'Hors Garantie'
        return {'value': {'date_end_warranty': date_end, 'warranty': warranty}}

    def create(self, cr, uid, vals, context=None):
        if 'ref' in vals and vals['ref'] and 'date_start_warranty' in vals and vals['date_start_warranty']:
            if vals['ref'].split(',')[0] == 'stock.production.lot':
                model = vals['ref'].split(',')[0]
                id = vals['ref'].split(',')[1]
                lot = self.pool.get(model).browse(cr, uid, int(id))
                for l in lot:
                    date_end = datetime.strptime(vals['date_start_warranty'], '%Y-%m-%d') + relativedelta(months=int(l.product_id.warranty), days=-1)
                vals['date_end_warranty'] = date_end
                if datetime.strptime(vals['date'], '%Y-%m-%d %H:%M:%S') > date_end:
                    vals['warranty'] = 'Hors Garantie'
        return super(crm_claim, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        lot = {}
        if 'ref' in vals:
            if vals['ref'].split(',')[0] == 'stock.production.lot':
                id = vals['ref'].split(',')[1]
                lot = self.pool.get('stock.production.lot').browse(cr, uid, int(id))
        else:
            lot = self.browse(cr, uid, ids).ref
            if lot._model != 'stock.production.lot':
                return super(crm_claim, self).write(cr, uid, ids, vals, context=context)
        if 'date_start_warranty' in vals:
            date_start_warranty = vals['date_start_warranty']
        else:
            date_start_warranty = self.browse(cr, uid, ids).date_start_warranty
        if 'date' in vals:
            date = vals['date']
        else:
            date = self.browse(cr, uid, ids).date
        for l in lot:
            date_end = datetime.strptime(date_start_warranty, '%Y-%m-%d') + relativedelta(months=int(l.product_id.warranty), days=-1)
            vals['date_end_warranty'] = date_end
            vals['warranty'] = ''
            if datetime.strptime(date, '%Y-%m-%d %H:%M:%S') > date_end:
                vals['warranty'] = 'Hors Garantie'
        return super(crm_claim, self).write(cr, uid, ids, vals, context=context)