# -*- encoding: utf-8 -*-
###############################################################################
#                                                                             #
# product_brand for Odoo                                                      #
# Copyright (C) 2009 NetAndCo (<http://www.netandco.net>).                    #
# Copyright (C) 2011 Akretion Benoît Guillot <benoit.guillot@akretion.com>    #
# Copyright (C) 2014 prisnet.ch Seraphine Lantible <s.lantible@gmail.com>     #
# Copyright (C) 2015 Leonardo Donelli                                         #
# Contributors                                                                #
# Mathieu Lemercier, mathieu@netandco.net                                     #
# Franck Bret, franck@netandco.net                                            #
# Seraphine Lantible, s.lantible@gmail.com, http://www.prisnet.ch             #
# Leonardo Donelli, donelli@webmonks.it, http://www.wearemonk.com             #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU Affero General Public License as              #
# published by the Free Software Foundation, either version 3 of the          #
# License, or (at your option) any later version.                             #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the                #
# GNU Affero General Public License for more details.                         #
#                                                                             #
# You should have received a copy of the GNU Affero General Public License    #
# along with this program. If not, see <http://www.gnu.org/licenses/>.        #
#                                                                             #
###############################################################################
###############################################################################
# Product Brand is an Openobject module wich enable Brand management for      #
# products                                                                    #
###############################################################################
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.osv import osv
from openerp import SUPERUSER_ID

class product_pricelist(models.Model):
    _inherit = "product.template"

    wholesale_price = fields.Float('Wholesale Price', digits_compute=dp.get_precision('Product Price'))
    details_price = fields.Float('Details Price', digits_compute=dp.get_precision('Product Price'))
    cash_price = fields.Float('Cash Price', digits_compute=dp.get_precision('Product Price'))

class sale_order_line(models.Model):
    _inherit = "sale.order.line"

    @api.multi
    def onchange_amount(self, price_unit, product_id):
        v = {}
        if not product_id:
            return {'value': v}
        product = self.env['product.product'].browse(product_id)
        if product.wholesale_price > price_unit:
            if self._uid == SUPERUSER_ID or self.pool['res.users'].has_group(self._cr, self._uid, 'pricelist_extension.group_limit_price_unit'):
                raise osv.except_osv(_('Warning!'), _('The wholesale price of %s is %s which is higher than the price indicate %s !') % (product.name, product.wholesale_price, price_unit))
            else:
                return {'value': {'price_unit': product.wholesale_price}, 'warning': {'title': _('Warning!'), 'message': _('The wholesale price of %s is %s which is higher than the price indicate %s. \n  '
                                                                                                                           'Insufficient permission! the price will be returned to %s!') % (product.name, product.wholesale_price, price_unit, product.wholesale_price)}}