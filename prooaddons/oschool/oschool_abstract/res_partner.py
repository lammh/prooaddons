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
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'
    _order = 'name asc'

    category = fields.Char('Category', compute="_get_category", store=True)
    #coordonée de parnet si il est défini
    p_phone = fields.Char('Phone', compute="_get_info")
    p_phone2 = fields.Char('Phone 2', compute="_get_info")
    p_mobile = fields.Char('Mobile', compute="_get_info")
    p_mobile2 = fields.Char('Mobile 2', compute="_get_info")
    p_mail = fields.Char('e-Mail', compute="_get_info")

    @api.one
    @api.depends('parent_id')
    def _get_info(self):
        if self.parent_id:
            self.p_phone = self.parent_id.phone
            self.p_phone2 = self.parent_id.phone2
            self.p_mobile = self.parent_id.mobile
            self.p_mobile2 = self.parent_id.mobile2
            self.p_mail = self.parent_id.email

    @api.one
    @api.depends('property_product_pricelist')
    def _get_category(self):
        self.category = self.property_product_pricelist.name



    @api.constrains('name', 'last_name', 'parent_id')
    def _check_name(self):
        for record in self:
            ids = self.search([('name','=',record.name),
                         ('last_name','=',record.last_name),
                         ('parent_id','=',record.parent_id.id),
                         ])
            if len(ids) > 1:
                raise ValidationError("This student already exists!")
    #On intercepte le changement de la catégorie de parent
    #pour changer le prix des abonnement non payé
    #on respecte la régle apply_price_list pour la période
    @api.one
    def write(self, vals):
        result = super(res_partner, self).write(vals)
        if 'property_product_pricelist' in vals:
            lines = self.env['pos.order.line'].search([('parent_id','=',self.id),('order_id', '=', False)])
            for line in lines:
                if line.period_id.apply_price_list:
                    inv = line.onchange_product_id(
                                                   line.student_id.parent_id.property_product_pricelist.id,
                                                   line.product_id.id,
                                                   1,
                                                   line.student_id.parent_id.id)
                else:
                    list0 = self.env['ir.model.data'].get_object_reference('product', 'list0')
                    inv = line.onchange_product_id(
                        list0[1],
                        line.product_id.id,
                        line.qty,
                        line.student_id.parent_id.id)
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
        if 'class_id' in vals:
            restaurants = self.env['oschool.student_restaurant_presence'].search([('student_id','=',self.id),
                                                                                 ('academic_year', '=', self.academic_year_id.id)])
            for restaurant in restaurants:
                restaurant.write({'class_id':vals['class_id']})

            canteens = self.env['oschool.student_canteen_presence'].search([('student_id','=',self.id),
                                                                                 ('academic_year', '=', self.academic_year_id.id)])
            for canteen in canteens:
                canteen.write({'class_id':vals['class_id']})
            #mettre a jour le classe de l'éléve dans les pos_order_line lors de la modification de son classe
            lines = self.env['pos.order.line'].search([('student_id','=',self.id),('order_id', '=', False)])
            for line in lines:
                line.write({'class_id':vals['class_id']})
        #mettre a jour le parent de l'éléve dans les pos_order_line lors de la modification de son parent
        if 'parent_id' in vals:
            lines = self.env['pos.order.line'].search([('student_id','=',self.id),('order_id', '=', False)])
            for line in lines:
                if line.period_id.apply_price_list:
                    inv = line.onchange_product_id(
                                                   line.student_id.parent_id.property_product_pricelist.id,
                                                   line.product_id.id,
                                                   1,
                                                   line.student_id.parent_id.id)
                else:
                    list0 = self.env['ir.model.data'].get_object_reference('product', 'list0')
                    inv = line.onchange_product_id(
                        list0[1],
                        line.product_id.id,
                        line.qty,
                        line.student_id.parent_id.id)
                line.write(inv['value'])


        return result