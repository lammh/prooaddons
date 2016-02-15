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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp

class invoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity', 'price_ht',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        self.price_subtotal_ttc = self.invoice_id.currency_id.round(taxes['total_included'])
        self.price_ht = self.invoice_line_tax_id.compute_all(price, 1, product=self.product_id, partner=self.invoice_id.partner_id)['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)

    price_ht = fields.Float(string='Amount HT', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')

    price_subtotal_ttc = fields.Float(string='Amount TTC', digits= dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')
