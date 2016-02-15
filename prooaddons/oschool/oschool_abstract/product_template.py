# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
#/#############################################################################
from openerp import models, fields, api, exceptions, _
import logging
_logger = logging.getLogger(__name__)

class product_template(models.Model):
    _inherit = 'product.template'

    #On intercepte le changement de prix de produit
    #pour changer le prix des abonnement non payé
    #on respecte la régle apply_price_list pour la période
    @api.one
    def write(self, vals):
        result = super(product_template, self).write(vals)
        if 'list_price' in vals:
            lines = self.env['pos.order.line'].search([('product_id.product_tmpl_id','=',self.id),
                                                   ('order_id', '=', False)])
            product_id = self.env['product.product'].search([('product_tmpl_id','=',self.id)]).id
            for line in lines:
                if line.period_id.apply_price_list:
                    inv = line.onchange_product_id(
                                                   line.student_id.parent_id.property_product_pricelist.id,
                                                   product_id,
                                                   1,
                                                   line.student_id.parent_id.id)
                else:
                    list0 = self.env['ir.model.data'].get_object_reference('product', 'list0')
                    inv = line.onchange_product_id(
                        list0[1],
                        line.product_id.id,
                        line.qty,
                        line.parent_id)
                inv['value']['academic_year_id'] = line.student_id.academic_year_id.id
                inv['value']['product_id'] = line.product_id.id
                inv['value']['product_id_tmpl'] = line.product_id_tmpl.id
                inv['value']['group_id'] = line.student_id.group_id.id
                inv['value']['class_id'] = line.student_id.class_id.id
                inv['value']['student_id'] = line.student_id.id
                inv['value']['parent_id'] = line.student_id.parent_id.id
                inv['value']['type'] = line.type
                inv['value']['qty'] = line.qty
                inv['value']['period_id'] = line.period_id.id
                inv['value']['discount_on_product'] = float(line.product_id.list_price - inv['value']['price_unit'])


                line.write(inv['value'])
        return result