from openerp import models, fields, api, _
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm

class stock_production_lot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('name', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name2', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = record['name']
            if record['name2']:
                name = name + '/' + record['name2']
            if record['ref']:
                name = name + ' (' + record['ref'] + ')'
            res.append((record['id'], name))
        return res

    name2 = fields.Char('Serial Number', help="Unique Serial Number 2")

class split_in_production_lot(osv.osv_memory):
    _inherit = "stock.move.split"

    def split(self, cr, uid, ids, move_ids, context=None):
        """ To split stock moves into serial numbers

        :param move_ids: the ID or list of IDs of stock move we want to split
        """
        if context is None:
            context = {}
        assert context.get('active_model') == 'stock.move',\
             'Incorrect use of the stock move split wizard'

        prodlot_obj = self.pool.get('stock.production.lot')
        packope_obj = self.pool.get('stock.pack.operation')
        move_obj = self.pool.get('stock.move')
        new_move = []
        for data in self.browse(cr, uid, ids, context=context):
            for move in move_obj.browse(cr, uid, move_ids, context=context):
                self.pool.get('stock.picking').do_enter_transfer_details(cr, uid, [move.picking_id.id])
                packope = packope_obj.search(cr, uid, [('picking_id', '=', move.picking_id.id), ('product_id', '=', move.product_id.id), ('product_qty', '=', move.product_qty)], limit=1)[0]

                move_qty = move.product_qty
                quantity_rest = move.product_qty
                uos_qty_rest = move.product_uos_qty
                new_move = []
                lines = [l for l in data.line_ids if l]
                total_move_qty = 0.0
                for line in lines:
                    quantity = line.quantity
                    total_move_qty += quantity
                    if total_move_qty > move_qty:
                        raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                                % (total_move_qty, move.product_id.name, move_qty))
                    if quantity <= 0 or move_qty == 0:
                        continue
                    quantity_rest -= quantity
                    uos_qty = quantity / move_qty * move.product_uos_qty
                    uos_qty_rest = quantity_rest / move_qty * move.product_uos_qty
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        packope_obj.log(cr, uid, line, _('Unable to assign all lots to this move!'))
                        return False
                    default_val = {
                        'product_qty': quantity,
                    }
                    if quantity_rest > 0:
                        current_move = packope_obj.copy(cr, uid, packope, default_val, context=context)
                        new_move.append(current_move)

                    if quantity_rest == 0:
                        current_move = packope
                    prodlot_id = False
                    if data.use_exist:
                        prodlot_id = prodlot_obj.search(cr, uid, ['|', ('name', '=', line.name), ('name2', '=', line.name)])
                        if len(prodlot_id) > 0:
                            prodlot_id = prodlot_id[0]
                        else:
                            raise osv.except_osv(_('Error!'), _('Serial number %s is not exist!') % (line.name,))
                    if not prodlot_id:
                        prodlot_id = prodlot_obj.create(cr, uid, {
                            'name': line.name,
                            'product_id': move.product_id.id},
                        context=context)

                    packope_obj.write(cr, uid, [current_move], {'lot_id': prodlot_id})

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        packope_obj.write(cr, uid, packope, update_val)

        return new_move