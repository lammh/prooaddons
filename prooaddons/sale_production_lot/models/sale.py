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
    _name = 'sale.production.lot.line'

    name = fields.Many2one('sale.production.lot', 'Lot')
    prodlot_id = fields.Char('Lot', required=1)
    quantity = fields.Float('Quantity', required=1, default=1)

class sale_production_lot(models.Model):
    _name = 'sale.production.lot'

    name = fields.Char('Name')
    lots = fields.One2many('sale.production.lot.line', 'name')

    @api.one
    def sale_lot(self):
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        sale = sale_obj.browse(self._context.get('active_id'))
        exist = {}
        lots = []
        for line in self.lots:
            lot = self.env['stock.production.lot'].search(['|', ('name', '=', line.prodlot_id), ('name2', '=', line.prodlot_id)])
            if not lot:
                raise osv.except_osv(_('Error!'), _('%s not exist.') % (line.prodlot_id,))

            if lot not in lots:
                lots.append(lot)
            else:
                raise osv.except_osv(_('Error!'), _('Duplicate %s/%s.') % (lot.name, lot.name2))

            if lot.product_id.id in exist:
                exist[lot.product_id.id]['quantity'] += 1.0
            else:
                exist[lot.product_id.id] = {'quantity': 1}

        for product in exist.items():
            sale_line_obj.create({'order_id': sale.id, 'product_id': product[0], 'product_uom_qty': product[1]['quantity']})

        return True
