from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp

class stock_inventory(models.Model):
    _inherit =  "stock.inventory"

    lot = fields.Char('Lot')

    @api.one
    def lot_integration(self):
        production_lot_obj = self.env['stock.production.lot']
        products = production_lot_obj.search([('ref', '=', self.lot)])
        for lot in products:
            vals = {
                'product_id': lot.product_id.id,
                'location_id': self.location_id.id,
                'prod_lot_id': lot.id,
                'product_qty': 1,
                'inventory_id': self.id,
            }
            self.line_ids.create(vals)
        self.lot = ""
        return True