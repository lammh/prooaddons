from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm

class stock_picking(models.Model):
    _inherit = "stock.picking"
    

    @api.multi
    def update_location(self):
        if not self.location or not self.location_dest:
            raise except_orm(_('Warning!'), _('You cannot update location empty.'))
        for line in self.move_lines:
            line.location_id = self.location
        for line in self.move_lines:
            line.location_dest_id = self.location_dest
        return True

    location = fields.Many2one('stock.location', 'Source Location', states={'done': [('readonly', True)]},
                                       help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest = fields.Many2one('stock.location', 'Destination Location', states={'done': [('readonly', True)]},
                                            help="Location where the system will stock the finished products.")

class stock_transfer_details(models.TransientModel):
    _inherit = "stock.transfer_details"

    @api.multi
    def update_source(self):
        for det in self:
            for line in det.item_ids:
                line.sourceloc_id = self.location
        if self and self[0]:
            return self[0].wizard_view()

    @api.multi
    def update_dest(self):
        for det in self:
            for line in det.item_ids:
                line.destinationloc_id = self.location_dest
        if self and self[0]:
            return self[0].wizard_view()

    location = fields.Many2one('stock.location', 'Source Location',
                                       help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations.")
    location_dest = fields.Many2one('stock.location', 'Destination Location', help="Location where the system will stock the finished products.")

class stock_move(models.Model):
    _inherit = "stock.move"

    def onchange_product_id(self, cr, uid, ids, prod_id=False, loc_id=False, loc_dest_id=False, partner_id=False):
        res = super(stock_move, self).onchange_product_id(cr, uid, ids, prod_id, loc_id, loc_dest_id, partner_id)
        qty = self.onchange_location(cr, uid, ids, prod_id, loc_id, loc_dest_id)['value']
        if not res:
            return res
        res['value']['qty_source'] = qty['qty_source']
        res['value']['qty_dest'] = qty['qty_dest']
        return res

    def onchange_location(self, cr, uid, ids, product_id, location_id, location_dest_id, context=None):
        if not context:
            context = {}
        qty_source = 0.0
        qty_dest = 0.0
        product_obj = self.pool.get('product.product')
        ctx = context.copy()
        if not product_id:
            return {'value': {'qty_source': 0,'qty_dest': 0}}
        if location_id:
            ctx['location'] = location_id
            qty_source = product_obj._product_available(cr, uid, [product_id], context=ctx)[product_id]['qty_available']
        if location_dest_id:
            ctx['location'] = location_dest_id
            qty_dest = product_obj._product_available(cr, uid, [product_id], context=ctx)[product_id]['qty_available']
        return {'value': {'qty_source': qty_source, 'qty_dest': qty_dest}}

    @api.one
    def _get_qty(self):
        return {}

    qty_source = fields.Float(compute='_get_qty', string='Quantity', digits_compute=dp.get_precision('Product Unit of Measure'))
    qty_dest = fields.Float(compute='_get_qty', string='Quantity', digits_compute=dp.get_precision('Product Unit of Measure'))

