from openerp import models, fields, api, _
from openerp.osv import osv
from dateutil.relativedelta import relativedelta
from datetime import datetime

class crm_claim(models.Model):
    _inherit = "crm.claim"

    date_start_warranty = fields.Date('Warranty start date')
    date_end_warranty = fields.Date('Warranty end date')
    warranty = fields.Char('Warranty')

    @api.multi
    def onchange_warranty(self, ref, date_start_warranty, date):
        if not ref:
            return {}
        if ref.split(',')[0] != 'stock.production.lot':
            return {}
        model = ref.split(',')[0]
        id = ref.split(',')[1]
        lot = self.env[model].browse(int(id))
        for quant in lot.quant_ids:
            if quant.location_id.usage == 'customer':
                date_start_warranty = quant.in_date
        if not date_start_warranty:
            return {'value': {'warranty': 'Hors Garantie'}}
        for l in lot:
            date_end = datetime.strptime(date_start_warranty, '%Y-%m-%d') + relativedelta(months=int(l.product_id.warranty), days=-1)
        warranty = ''
        if datetime.strptime(date, '%Y-%m-%d %H:%M:%S') > date_end:
            warranty = 'Hors Garantie'
        return {'value': {'date_end_warranty': date_end, 'warranty': warranty, 'date_start_warranty': date_start_warranty}}

