# -*- encoding: utf-8 -*-
##############################################################################
#    
#    Odoo, Open Source Management Solution
#
#    Author: Andrius Laukavičius. Copyright: JSC NOD Baltic
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################

from openerp import models, fields, api, _
from openerp.osv import osv

class sale_production_lot(models.Model):
    _name = 'picking.production.lot.line'

    name = fields.Many2one('picking.production.lot', 'Lot')
    prodlot_id = fields.Char('Lot', required=1)
    quantity = fields.Float('Quantity', required=1, default=1)

class sale_production_lot(models.Model):
    _name = 'picking.production.lot'

    name = fields.Char('Name')
    lots = fields.One2many('picking.production.lot.line', 'name')

    @api.one
    def picking_lot(self):
        transfer_details = self.env['stock.transfer_details'].browse(self._context.get('active_id'))
        picking = self.env['stock.transfer_details'].browse(self._context.get('active_id')).picking_id
        pack_operation_obj = self.env['stock.pack.operation']
        exist = {}
        location_dest_id = None
        location_id = None
        for move in [x for x in picking.move_lines if x.state not in ('done', 'cancel')]:
            if not move.scrapped:
                if location_dest_id and move.location_dest_id.id != location_dest_id:
                    raise Warning(_('The destination location must be the same for all the moves of the picking.'))
                location_dest_id = move.location_dest_id.id
                if location_id and move.location_id.id != location_id:
                    raise Warning(_('The source location must be the same for all the moves of the picking.'))
                location_id = move.location_id.id

        lots = []
        for line in self.lots:
            lot = self.env['stock.production.lot'].search(['|', ('name', '=', line.prodlot_id), ('name2', '=', line.prodlot_id)])
            if not lot:
                raise osv.except_osv(_('Error!'), _('%s not exist.') % (line.prodlot_id,))
            if lot not in lots:
                lots.append(lot)
            else:
                raise osv.except_osv(_('Error!'), _('Duplicate %s/%s.') % (lot.name, lot.name2))

            for item in pack_operation_obj.search([('picking_id', '=', picking.id), ('product_id', '=', lot.product_id.id), ('lot_id', '=', False)], limit=1):
                item.product_qty -= 1
                if item.product_qty == 0:
                    item.unlink()

            pack_operation_obj.create({'picking_id': picking.id,
                                       'product_id': lot.product_id.id,
                                       'product_qty': line.quantity,
                                       'location_id': location_id,
                                       'location_dest_id': location_dest_id,
                                       'product_uom_id': self.env['product.product'].browse(lot.product_id.id).uom_id.id,
                                       'lot_id': lot.id,
                                       })

        return {'type': 'ir.actions.act_window_close'}

