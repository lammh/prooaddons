from openerp.osv import fields, osv
from openerp import models
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class stock_move(models.Model):
    _inherit =  "stock.move"

    def create(self, cr, uid, vals, context=None):
        if 'procurement_id' in vals:
            procurement = self.pool.get('procurement.order').browse(cr, uid, vals['procurement_id'])
            if procurement.sale_line_id:
                vendor = procurement.sale_line_id.order_id.user_id.partner_id.id
                location_id = self.pool.get('stock.location').search(cr, uid, [('partner_id', '=', vendor)], limit=1)
                if location_id:
                    vals['location_id'] = location_id[0]

        return super(stock_move, self).create(cr, uid, vals, context=context)

