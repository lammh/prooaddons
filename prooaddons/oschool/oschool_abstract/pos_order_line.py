# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class pos_order_line(models.Model):
    _inherit = 'pos.order.line'

    state = fields.Char('state', compute="_get_state")
    product_category_id = fields.Many2one('product.category', string='Category of Product')

    phone = fields.Char('Phone', compute="_get_info")
    phone2 = fields.Char('Phone 2', compute="_get_info")
    mobile = fields.Char('Mobile', compute="_get_info")
    mobile2 = fields.Char('Mobile 2', compute="_get_info")
    mail = fields.Char('e-Mail', compute="_get_info")
    date_order = fields.Datetime('Date order', compute="_get_state", store=True)
    #un champ pour calculer le remise fait sur un abonnement
    discount_on_product = fields.Float('Discount', readonly=True)


    @api.one
    @api.depends('parent_id')
    def _get_info(self):
        self.phone = self.parent_id.phone
        self.phone2 = self.parent_id.phone2
        self.mobile = self.parent_id.mobile
        self.mobile2 = self.parent_id.mobile2
        self.mail = self.parent_id.email


    @api.one
    @api.depends('order_id')
    def _get_state(self):
        if self.order_id:
            self.state = self.order_id.state
            self.date_order = self.order_id.date_order

    @api.one
    @api.depends('product_id')
    def _get_product_categ(self):
        self.product_category_id = self.product_id.product_tmpl_id.pos_categ_id.product_category.name



    def create(self,cr,uid, vals, context=None):
        product_obj = self.pool.get('product.product')

        if 'period_id' in vals and 'parent_id' in vals and 'qty' in vals and 'product_id' in vals:
            period = self.pool.get('account.period').browse(cr, uid, vals['period_id'])
            if not period.apply_price_list:
                list0 = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'product', 'list0')
                inv = self.onchange_product_id(cr, uid, vals['product_id'], list0[1], vals['product_id'], vals['qty'], vals['parent_id'])
                vals['price_unit'] = inv['value']['price_unit']
                vals['price_subtotal'] = inv['value']['price_subtotal']
                vals['price_subtotal_incl'] = inv['value']['price_subtotal_incl']
                inv['value']['discount_on_product'] = float(product_obj.browse(cr, uid, vals['product_id']).list_price - inv['value']['price_unit'])

        return super(pos_order_line,self).create(cr,uid, vals,context)
