# -*- coding: utf-8 -*-
##############################################################################
#
#  OpenERP, CRM Claim Report Extension
#  Copyright (c) 2014  Enterprise Objects Consulting
#  All Rights Reserved.
#
#  Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "CRM Claim Report Extension",
    "version" : "0.2",
    "author": "Enterprise Objects Consulting",
    "website": "http://www.eoconsulting.com.ar",
    "license" : "AGPL-3",
    "category" : "Customer Relationship Management",
    "description": """
Add a PDF report to CRM Claims.

It's compatible (optional) with the following modules (show additional fields
of this modules if are installed):

* crm_claim_sequence
* crm_claim_serial_number
    """,
    "depends" : [
            "crm_claim",
        ],
    "update_xml" : [
            'report/crm_claim_report.xml',
        ],
    "images" : [
            'images/crm_claim_report.gif',
        ],
    "installable": True,
    "active": False,
}
