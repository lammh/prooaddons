# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    "name": "Cancel Invoice & voucher Groups",
    "version": "1.0",
    "category": "Accounting & Finance",
    "author": "Digitec",
    "website": "http://www.digitecsys.com",
    "license": "AGPL-3",
    "depends": [
        'account_cancel',
        'account_voucher',
        'l10n_tn_taxes',
    ],
    "data": [
        'security/security.xml',
        'invoice_voucher_view.xml',
    ],
    'installable': True,
}
