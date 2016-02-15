# -*- coding: utf-8 -*-
##############################################################################
#
#  OpenERP, CRM Claim Sequence
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
    "name" : "CRM Claim Sequence",
    "version" : "0.1",
    "author": "Enterprise Objects Consulting",
    "website": "http://www.eoconsulting.com.ar",
    "license" : "AGPL-3",
    "category" : "Customer Relationship Management",
    "description": """
This module allows to associate a sequence to a CRM Claim.

The new "Number" field is unique (SQL constraint) and required.
    """,
    "depends" : [
            "crm_claim",
        ],
    "init_xml" : [
            "crm_claim_sequence.xml",
        ],
    "update_xml" : [
            "crm_claim_view.xml",
        ],
    "installable": True,
    "active": False,
}
