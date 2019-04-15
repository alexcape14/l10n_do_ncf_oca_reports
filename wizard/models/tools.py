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

"""
Funciones tools para el modulo ncf_dgii_reports
"""
import datetime
import re

from odoo import api

TODAY = datetime.date.today()

FORMA_DE_PAGO = [
    ('01', 'cash'),
    ('02', 'bank'),
    ('03', 'card'),
    ('04', 'credit'),
    ('05', 'swap'),
    ('06', 'bond'),
    ('07', 'others')]


@api.model
def gen_years(self):
    """
    Genera una lista years hasta el year acutal.
    """
    yearls = []
    date_start = datetime.date(2000, 1, 1)
    today = datetime.date.today()
    for item in range(today.year - date_start.year + 1):
        year_id = year_label = str(date_start.year + item)
        yearls.append((year_id, year_label))
    yearls.reverse()
    return yearls


@api.model
def gen_months(self):
    """
    Genera una lista del 1 al 12 que representa los 12 meses del year.
    """
    return [(str(i), str(i)) for i in range(1, 13)]


@api.model
def today(self):
    return datetime.date.today()


@api.model
def gen_txt(self):
    pass


@api.model
def get_type_identification(self, vat):
    rnc_schedule = vat and re.sub("[^0-9]", "", vat.strip()) or False
    identification_type = "3"
    if rnc_schedule:
        if len(rnc_schedule) == 9:
            identification_type = "1"
        elif len(rnc_schedule) == 11:
            identification_type = "2"

    if identification_type == "3":
        rnc_schedule = ""

    return rnc_schedule, identification_type


@api.model
def get_all_invoice(self, start_date, end_date):
    """
    Esta funcion retorna todas las facturas de una fecha inicial a una final.
    """
    invoice_ids = self.env["account.invoice"] \
        .search([('date_invoice', '>=', start_date),
                 ('date_invoice', '<=', end_date)])
    return invoice_ids


@api.model
def get_all_payments(self, start_date, end_date, has_invoice=True):
    paid_invoice_ids = self.env["account.payment"] \
        .search([('payment_date', '>=', start_date),
                 ('payment_date', '<=', end_date),
                 ('has_invoice', '=', has_invoice)])
    return paid_invoice_ids


@api.multi
def post_error_list(self, error_list):
    out_inovice_url = "/web#id={}&view_type=form&model=account.invoice&action=196"
    in_inovice_url = "/web#id={}&view_type=form&model=account.invoice&menu_id=119&action=197"
    if error_list:
        message = "<ul>"
        for ncf, errors in error_list.iteritems():
            message += "<li>{}</li><ul>".format(errors[0][1] or "Factura invalida")
            for error in errors:
                if error[0] in ("out_invoice", "out_refund"):
                    message += u"<li><a target='_blank' href='{}'>{}</a></li>".format(out_inovice_url.format(ncf),
                                                                                      error[2])
                else:
                    message += u"<li><a target='_blank' href='{}'>{}</a></li>".format(in_inovice_url.format(ncf),
                                                                                      error[2])
            message += "</ul>"
        message += "</ul>"

        self.message_post(body=message)
        self.state = "error"
    else:
        self.message_post(body="Generado correctamente")
        self.state = "done"
