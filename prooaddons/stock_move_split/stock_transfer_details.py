import logging
from openerp.osv import osv
from openerp import models, fields, api, SUPERUSER_ID
from openerp.api import Environment
from openerp.tools.translate import _
from openerp.exceptions import except_orm
import openerp.addons.decimal_precision as dp
from datetime import datetime
import time

_logger = logging.getLogger(__name__)

class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(stock_transfer_details, self).default_get(cr, uid, fields, context=context)
        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('stock.picking'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('stock.picking').browse(cr, uid, picking_id, context=context)
        items = []
        packs = []
        if not picking.pack_operation_ids:
            picking.do_prepare_partial()
        for op in picking.pack_operation_ids:
            item = {
                'packop_id': op.id,
                'product_id': op.product_id.id,
                'product_uom_id': op.product_uom_id.id,
                'quantity': op.product_qty,
                'package_id': op.package_id.id,
                'lot_id': op.lot_id.name,
                'sourceloc_id': op.location_id.id,
                'destinationloc_id': op.location_dest_id.id,
                'result_package_id': op.result_package_id.id,
                'date': op.date,
                'owner_id': op.owner_id.id,
            }
            if op.product_id:
                items.append(item)
            elif op.package_id:
                packs.append(item)
        res.update(item_ids=items)
        res.update(packop_ids=packs)
        return res

    @api.one
    def do_detailed_transfer(self):
        for det in self.item_ids:
            if det.first_lot and det.last_lot:
                serials = self.env['stock.production.lot'].search(['&', '&', ('product_id', '=', det.product_id.id), ('ref', '>=', det.first_lot), ('ref', '<=', det.last_lot)])
                if len(serials) != det.quantity:
                    raise except_orm(_('Data Error!'), _("Quantity in lots between %s and %s is %s") % (det.first_lot, det.last_lot, len(serials)))
                for serial in serials:
                    if det.quantity >= 1:
                        det.quantity = (det.quantity-1)
                        new_id = det.copy(context=self.env.context)
                        new_id.quantity = 1
                        new_id.packop_id = False
                        new_id.lot_id = serial.name
                if det.quantity == 0:
                    det.unlink()

        processed_ids = []
        ctx = self._context.copy()
        ctx['no_recompute'] = True
        lot_obj = self.env['stock.production.lot']
        # Create new and update existing pack operations
        for lstits in [self.item_ids, self.packop_ids]:
            len_list = len(lstits) - 1
            for prod in lstits:
                lot_id = False
                if prod.lot_id:
                    lot_id = lot_obj.search(['&', ('product_id', '=', prod.product_id.id), '|', ('name', '=', prod.lot_id), ('name2', '=', prod.lot_id)])
                    if lot_id:
                        lot_id = lot_id[0].id
                    else:
                        raise osv.except_osv(_('Warning!'), _('non-existent serial number %s for %s.') % (prod.lot_id, prod.product_id.name))
                pack_datas = {
                    'product_id': prod.product_id.id,
                    'product_uom_id': prod.product_uom_id.id,
                    'product_qty': prod.quantity,
                    'package_id': prod.package_id.id,
                    'lot_id': lot_id,
                    'location_id': prod.sourceloc_id.id,
                    'location_dest_id': prod.destinationloc_id.id,
                    'result_package_id': prod.result_package_id.id,
                    'date': prod.date if prod.date else datetime.now(),
                    'owner_id': prod.owner_id.id,
                }
                if prod.packop_id:
                    prod.packop_id.write(pack_datas)
                    processed_ids.append(prod.packop_id.id)
                else:
                    pack_datas['picking_id'] = self.picking_id.id
                    if len(processed_ids) < len_list:
                        packop_id = self.pool.get('stock.pack.operation').create(self._cr, self._uid, pack_datas, context=ctx)
                    else:
                        packop_id = self.env['stock.pack.operation'].create(pack_datas).id
                    processed_ids.append(packop_id)

        # Delete the others
        packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
        for packop in packops:
            packop.unlink()

        # Execute the transfer of the picking
        self.picking_id.do_transfer()
        return True


class stock_transfer_details_items(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    first_lot = fields.Char(string="First Lot")
    last_lot = fields.Char(string="Last Lot")
    lot_id = fields.Char('Lot/Serial Number')