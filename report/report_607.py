# -*- coding: utf-8 -*-
# © 2015-2018 Marcos Organizador de Negocios SRL. (https://marcos.do/)

#             Eneldo Serrata <eneldo@marcos.do>
# © 2018-2019 SoftNet Team SRL. (https://www.softnet.do/)
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
# ######################################################################.
"""
Reporte de vetas 607 para la DGII
"""
import logging

from odoo import fields, models, api

from .tools import gen_years, gen_months, TODAY

_logger = logging.getLogger(__name__)


class DgiiReport607(models.Model):
    _name = 'dgii.report.607'
    _description = "Reporte de ventas DGII 607"

    company_id = fields.Many2one(
            comodel_name='res.company',
            string='Empresa',
            default=lambda self:
            self.env['res.company']._company_default_get('dgii.report.607'),
            required=True)
    report_607_line = fields.One2many('report.607.line', 'dgii_report_607_id')
    count_register = fields.Integer('Cantidad de Registros')
    rnc_or_schedule = fields.Char('RNC',
                                  size=11,
                                  related='company_id.partner_id.vat',
                                  required=True)
    year = fields.Selection(gen_years, required=True, index=True,
                            default=lambda self: str(TODAY.year))
    month = fields.Selection(gen_months, required=True, index=True,
                             default=lambda self: str(TODAY.month - 1), store=True)
    state = fields.Selection(
            [('draft', 'Nuevo'),
             ('error', 'Con errores'),
             ('done', 'Valido')], default='draft')

    @api.multi
    @api.depends('report_607_line')
    def _compute_count_register(self):
        _logger.info("compute count register 607")
        for rec in self:
            rec.count_register = rec.report_607_line and \
                    len(rec.report_607_line)


class Report607Line(models.Model):
    _name = 'report.607.line'
    _description = "Lineas eportes de ventas DGII 607"

    line = fields.Integer("Linea")
    dgii_report_607_id = fields.Many2one('dgii.report.607')
    invoice_id = fields.Many2one('account.invoice', 'NCF')
    is_credit_note = fields.Boolean()
    rnc_or_schedule = fields.Char("RNC", size=11,
                                  related='invoice_id.partner_id.vat')
    identification_type = fields.Char("Tipo ID", size=1)
    ncf = fields.Char('NCF', size=19)
    modified_ncf = fields.Char('NCF Modificado', size=19)
    type_of_income = fields.Char('tipo de Ingreso', size=1)
    voucher_date = fields.Date('Fecha Comprobante')
    retention_date = fields.Date(u'Fecha de Retención')
    billed_amount = fields.Float('Monto Facturado')
    billed_itbis = fields.Float('ITBIS Facturado')
    retained_itbis = fields.Float('ITBIS Retenido')
    billed_amount = fields.Float('Monto Facturado')
    billed_itbis = fields.Float('ITBIS Facturado')
    retained_itbis = fields.Float('ITBIS Retenido')
    perceived_itbis = fields.Float('ITBIS Percibido')
    withholding_income_by_third_parties = fields.Float(u'Retención Renta por Terceros')
    perceived_isr = fields.Char('ISR Percibido')
    exicise_tax = fields.Float('Impuesto Selectivo al Consumo')
    other_tip_fees = fields.Float('Otros Impuesto/Tasas')
    legal_tip_amount = fields.Float('Monto Propina Legal')
    cash = fields.Float('Efectivo')
    check_transfer_deposit = fields.Float('Cheque/ Transferencia/ Depósito')
    debit_credit_card = fields.Float('Tarjeta Débito/Crédito')
