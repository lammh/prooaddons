from openerp.osv import fields, osv
from openerp import models
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class split_in_production_lot(osv.osv_memory):
    _name = "stock.move.split"
    _description = "Split in Serial Numbers"

    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        res = super(split_in_production_lot, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            move = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context=context)
            if 'product_id' in fields:
                res.update({'product_id': move.product_id.id})
            if 'product_uom' in fields:
                res.update({'product_uom': move.product_uom.id})
            if 'qty' in fields:
                res.update({'qty': move.product_qty})
            if 'use_exist' in fields:
                res.update({'use_exist': (move.location_id.usage != 'supplier' and True) or False})
            if 'location_id' in fields:
                res.update({'location_id': move.location_id.id})
        return res

    _columns = {
        'qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure'),
        'line_ids': fields.one2many('stock.move.split.lines', 'wizard_id', 'Serial Numbers'),
        'use_exist' : fields.boolean('Existing Serial Numbers',
            help="Check this option to select existing serial numbers in the list below, otherwise you should enter new ones line by line."),
        'location_id': fields.many2one('stock.location', 'Source Location')
     }

    def split_lot(self, cr, uid, ids, context=None):
        """ To split a lot"""
        if context is None:
            context = {}
        res = self.split(cr, uid, ids, context.get('active_ids'), context=context)
        return {'type': 'ir.actions.act_window_close'}

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
                        prodlot_id = prodlot_obj.search(cr, uid, [('name', '=', line.name), ('product_id', '=', move.product_id.id)])
                        if len(prodlot_id) > 0:
                            prodlot_id = prodlot_id[0]
                        else:
                            raise osv.except_osv(_('Error!'), _('Serial number %s is not exist for %s!') % (line.name,('product_id', '=', move.product_id.name)))
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

split_in_production_lot()

class stock_move_split_lines_exist(osv.osv_memory):
    _name = "stock.move.split.lines"
    _description = "Stock move Split lines"
    _columns = {
        'name': fields.char('Serial Number', size=64),
        'quantity': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure')),
        'wizard_id': fields.many2one('stock.move.split', 'Parent Wizard'),
        'wizard_exist_id': fields.many2one('stock.move.split', 'Parent Wizard (for existing lines)'),
        'prodlot_id': fields.many2one('stock.production.lot', 'Serial Number', change_default=True),
    }
    _defaults = {
        'quantity': 1.0,
    }

class stock_production_lot(models.Model):
    _inherit =  "stock.production.lot"

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name', 'ref'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['ref']:
                name = name + ' (' + record['ref'] + ')'
            res.append((record['id'], name ))
        return res

