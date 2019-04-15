# -*- coding: utf-8 -*-
# © 2015-2018 Marcos Organizador de Negocios SRL. (https://marcos.do/)

#             Eneldo Serrata <eneldo@marcos.do>
# © 2018 SoftNet Team SRL. (https://www.softnet.do/)
#             Manuel Gonzalez <manuel@softnet.do>

# © 2018 Jeffry Jesus De La Rosa <jeffryjesus@gmail.com>

# This file is part of NCF DGII Reports
# NCF DGII Reports is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# NCF DGII Reports is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with NCF DGII Reports.  If not, see <http://www.gnu.org/licenses/>.
# ######################################################################
{
    'name': "Reportes de Comprobantes Fiscales (NCF DGII Reports)",
    'version': '11.0.1.0.0',

    'summary': u"""
            Este módulo implementa los reportes de los números de
             comprobantes fiscales para el cumplimento de la norma 06-18 de la
             Dirección de Impuestos Internos en la República Dominicana.
        """,

    'author': "Marcos Organizador de Negocios SRL, "
              "SoftNet Team SRL, "
              "Odoo Dominicana (ODOM), "
              "Jeffry J. De La Rosa ",

    'category': 'Accounting',
# any module necessary for this one to work correctly

    'depends': ['base', 'account_invoicing', 'ncf_manager', 'ncf_invoice_template'],

    'data': [
        'data/invoice_service_type_detail_data.xml',
        'data/account_account_tag_data_more.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/res_partner_views.xml',
        'views/account_view.xml',
        'views/account_account_views.xml',
        'views/account_invoice_views.xml',
        'views/dgii_report_views.xml',
        'views/dgii_report_templates.xml',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
