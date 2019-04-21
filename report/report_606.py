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
# ######################################################################.e.

"""
Reporte de compras 606 para la DGII
"""
import logging
import calendar
import re
import base64

from odoo import models, fields, api, exceptions

from .tools import (gen_months, gen_years, TODAY, get_all_invoice,
                    get_type_identification)

_logger = logging.getLogger(__name__)


class DgiiReport606(models.Model):
    _name = 'dgii.report.606' #TODO ask to Jeffrey about this model.
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Referencia")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        default=lambda self:
        self.env['res.company']._company_default_get('dgii.report.606'),
        required=True)
    report_606_line = fields.One2many('report.606.line', 'dgii_report_606_id')
    count_register = fields.Integer(string='Cantidad de Registros',
                                    compute='_compute_count_register',
                                    store=True)
    rnc_or_schedule = fields.Char("RNC",
                                  size=11,
                                  related='company_id.partner_id.vat',
                                  required=True)
    year = fields.Selection(gen_years, required=True, index=True,
                            default=lambda self: str(TODAY.year))
    month = fields.Selection(gen_months, required=True, index=True,
                             default=lambda self: str(TODAY.month - 1))
    itbis_total = fields.Float(u"ITBIS Compras",
                               compute='_purchase_report_totals')
    itbis_total_nc = fields.Float(u"ITBIS Notas de crédito",
                                  compute='_purchase_report_totals')
    itbis_total_payment = fields.Float(u"ITBIS Pagado",
                                       compute='_purchase_report_totals')
    total_amount_billed = fields.Float(u"Monto compra",
                                       compute='_purchase_report_totals')
    total_amount_nc = fields.Float(u"Monto Notas decrédito",
                                   compute='_purchase_report_totals')
    TOTAL_MONTO_PAYMENT = fields.Float(u"Totalmonto facturado",
                                       compute='_purchase_report_totals')
    ITBIS_RETENIDO = fields.Float(u"ITBIS Retenido",
                                  compute='_purchase_report_totals')
    RETENCION_RENTA = fields.Float(u"Retención Renta",
                                   compute='_purchase_report_totals')
    purchase_filename = fields.Char()
    purchase_binary = fields.Binary(string=u"Archivo 606 TXT")
    state = fields.Selection(
        [('draft', 'Nuevo'),
         ('error', 'Con errores'),
         ('done', 'Valido')], string="Estado", default='draft')

    @api.depends("report_606_line")
    def _compute_count_register(self):
        self.count_register = len(self.mapped('report_606_line'))

    @api.multi
    @api.depends("report_606_line")
    def _purchase_report_totals(self):
        for record in self:
            _logger.info('_purchase_report_totals %s', record.report_606_line)
            record.itbis_total = 0
            record.itbis_total_nc = 0
            record.itbis_total_payment = 0
            record.total_amount_billed = 0
            record.total_amount_nc = 0
            record.TOTAL_MONTO_PAYMENT = 0
            record.ITBIS_RETENIDO = 0
            record.RETENCION_RENTA = 0
            for purchase in record.report_606_line:
                _logger.info('purchase billed itbis %s', purchase.billed_itbis)
                if purchase.modified_ncf:
                    record.itbis_total_nc += purchase.billed_itbis
                    record.total_amount_nc += purchase.total_charged
                else:
                    record.itbis_total += purchase.billed_itbis
                    record.total_amount_billed += purchase.total_charged
        return 0.0

    @api.multi
    def generate_report(self):
        try:
            year, month = self.year, self.month
            last_day = calendar.monthrange(int(year), int(month))[1]
            start_date = "{}-{}-01".format(year, month)
            end_date = "{}-{}-{}".format(year, month, last_day)

            self.name = "start:{} ; final:{}".format(start_date, end_date)

        except Exception:
            raise exceptions.ValidationError(u"Periodo invalido")

        self.report_606_line.unlink()

        purchase_line = 1
        invoice_ids = get_all_invoice(self, start_date, end_date)

        for invoice_id in invoice_ids:
            print("type de factura = ", invoice_id.type)
            print("invoice id = ", invoice_id.id)
            print("invoice number = ", invoice_id.number)
            print("purchase type = ", invoice_id.journal_id.purchase_type)
            print("invoice origin = ", invoice_id.origin)
            print("invoice refund_invoice_id = ", invoice_id.refund_invoice_id)

            if invoice_id.type in ("in_invoice", "in_refund") \
                    and invoice_id.state != 'cancel':

                data = {'dgii_report_606_id': self.id,
                        'invoice_id': invoice_id.id,
                        'line': purchase_line,
                        'billed_itbis': 0,
                        'amount_billed_in_services': 0,
                        'amount_billed_in_goods': 0,
                        'type_of_withholding_isr': None,
                        'total_charged': invoice_id.amount_untaxed,
                        'retained_itbis': 0,
                        'itbis_subject_to_proportionality': 0,
                        'itbis_taken_to_cost': 0,
                        'itbis_perceived_in_purchases': 0,
                        'income_withholding_amount': 0,
                        'isr_perceived_in_purchases': 0,
                        'exicise_tax': 0,
                        'other_tax_fees': 0,
                        'legal_tip_amount': 0}

                if invoice_id.type == "in_refund":
                    data['ncf'] = invoice_id.number or invoice_id.move_name
                    data['is_credit_note'] = True
                elif invoice_id.type == "in_invoice":
                    data['ncf'] = invoice_id.number or invoice_id.move_name
                    data['is_credit_note'] = False

                for inv_line in invoice_id.invoice_line_ids:
                    if inv_line.product_id.type in ('product', 'consu'):
                        data['amount_billed_in_goods'] += \
                                inv_line.price_subtotal
                    elif inv_line.product_id.type == 'service':
                        data['amount_billed_in_services'] += \
                                inv_line.price_subtotal

                for tax_line in invoice_id.tax_line_ids:
                    if tax_line.tax_id.purchase_tax_type == 'ritbis':
                        amount = tax_line.amount * -1 if tax_line.amount < 1\
                            else tax_line.amount
                        data['retained_itbis'] += amount

                    if tax_line.tax_id.purchase_tax_type == 'isr':
                        data['type_of_withholding_isr'] = \
                            tax_line.tax_id.isr_retention_type

                        amount = tax_line.amount * -1 if tax_line.amount < 1\
                            else tax_line.amount
                        data['income_withholding_amount'] += amount

                    if tax_line.tax_id.purchase_tax_type == 'none':
                        data['billed_itbis'] += tax_line.amount

                vat = get_type_identification(self, invoice_id.partner_id.vat)
                data['identification_type'] = vat[1]

                self.env['report.606.line'].create(data)
                purchase_line += 1

        self.gen_file_txt()

    @api.model
    def get_way_to_pay(self, report):
        shape = None
        if report.way_to_pay == 'cash':
            shape = '01'
        elif report.way_to_pay == 'bank':
            shape = '02'
        elif report.way_to_pay == 'card':
            shape = '03'
        elif report.way_to_pay == 'credit':
            shape = '04'
        elif report.way_to_pay == 'swap':
            shape = '05'
        elif report.way_to_pay == 'bond':
            shape = '06'
        elif report.way_to_pay == 'others':
            shape = '07'
        else:
            shape = '04'
        return shape

    def gen_file_txt(self):
        print('GENERANDO ARCHIVO')
        company_fiscal_identification = re.sub("[^0-9]", "",
                                               self.company_id.vat)
        periodo = str(self.year) + str(self.month).zfill(2)
        purchase_path = '/tmp/606{}.txt'.format(company_fiscal_identification)
        purchase_file = open(purchase_path, 'w')

        pipe = "|"
        lines = []

        data = ('606', str(self.rnc_or_schedule), periodo,
                str(self.count_register))
        header = pipe.join(data)
        lines.append(header)

        for report in self.report_606_line:
            data = []
            data.append(report.rnc_or_schedule)
            data.append(report.identification_type)
            data.append(report.type_purchased_goods_and_services)
            data.append(report.ncf)
            data.append(report.modified_ncf or "".rjust(19))
            data.append(report.voucher_date.replace("-", "") if report.voucher_date else "".rjust(8))
            data.append(report.payment_date.replace("-", "") if report.payment_date else "".rjust(8))
            data.append("{:.2f}".format(report.amount_billed_in_services).zfill(12))
            data.append("{:.2f}".format(report.amount_billed_in_goods).zfill(12))
            data.append("{:.2f}".format(report.total_charged).zfill(12))
            data.append("{:.2f}".format(report.billed_itbis).zfill(12))
            data.append("{:.2f}".format(report.retained_itbis).zfill(12))
            data.append("{:.2f}".format(report.itbis_subject_to_proportionality).zfill(12))
            data.append("{:.2f}".format(report.itbis_taken_to_cost).zfill(12))
            data.append("{:.2f}".format(report.itbis_to_advance).zfill(12))
            data.append("{:.2f}".format(report.itbis_perceived_in_purchases).zfill(12))
            data.append(report.type_of_withholding_isr or "00")
            data.append("{:.2f}".format(report.income_withholding_amount))
            data.append("{:.2f}".format(report.isr_perceived_in_purchases))
            data.append("{:.2f}".format(report.exicise_tax))
            data.append("{:.2f}".format(report.other_tax_fees))
            data.append("{:.2f}".format(report.legal_tip_amount))
            data.append(self.get_way_to_pay(report))

            lines.append(pipe.join(data))

        for line in lines:
            purchase_file.write(line + '\n')

        purchase_file.close()
        with open(purchase_path, 'rb') as purchase_file:
            self.write(
                    {'purchase_binary': base64.b64encode(purchase_file.read()),
                     'purchase_filename': 'DGII_F_606_{}_{}{}.TXT'.
                        format(company_fiscal_identification,
                               str(self.year),
                               str(self.month).zfill(2))})


class Report606Line(models.Model):
    _name = 'report.606.line'
    _description = 'Reporte de compras DGII 606' #TODO ask to Jeffrey about this model.

    line = fields.Integer("Linea")
    dgii_report_606_id = fields.Many2one("dgii.report.606")
    invoice_id = fields.Many2one("account.invoice", "NCF")
    is_credit_note = fields.Boolean()

    rnc_or_schedule = fields.Char("RNC", size=11,
                                  related='invoice_id.partner_id.vat')
    identification_type = fields.Char("Tipo ID", size=1)
    # ojo
    type_purchased_goods_and_services = fields.Selection(
        related='invoice_id.expense_type')
    ncf = fields.Char("NCF", size=19)
    modified_ncf = fields.Char("NCF Modificado", size=19,
                               related='invoice_id.origin')
    voucher_date = fields.Date("Fecha Comprobante",
                               related="invoice_id.date_invoice")
    payment_date = fields.Date("Fecha Pago",
                               related='invoice_id.payment_ids.payment_date')
    amount_billed_in_services = fields.Float("Monto Facturado en Servicios")
    amount_billed_in_goods = fields.Float("Monto Facturado en Bienes")
    total_charged = fields.Float("Total Monto Facturado")
    billed_itbis = fields.Float("ITBIS Facturado")
    retained_itbis = fields.Float("ITBIS Retenido")
    itbis_subject_to_proportionality = fields.Float("ITBIS sujeto a "
                                                    "Proporcionalidad "
                                                    "(Art. 349)")
    itbis_taken_to_cost = fields.Float("ITBIS llevado al Costo",
                                       help="Valor del ITBIS que no se deduce "
                                            "por concepto de adelanto en el "
                                            "Formulario de IT-1.")
    itbis_to_advance = fields.Float("ITBIS por Adelantar",
                                    related='billed_itbis')
    itbis_perceived_in_purchases = fields.Float("ITBIS percibido en compras",
                                                help="Desabilitado")
    type_of_withholding_isr = fields.Selection(
            [('01', 'Alquileres'),
             ('02', 'Honorarios por Servicios'),
             ('03', 'Otras Rentas'),
             ('04', 'Rentas Presuntas'),
             ('05', u'Intereses Pagados a Personas Jurídicas'),
             ('06', u'Intereses Pagados a Personas Físicas'),
             ('07', u'Retención por Proveedores del Estado'),
             ('08', u'Juegos Telefónicos')],
            "Tipo de Retención en ISR",
            help="Observacion")
    income_withholding_amount = fields.Float("Monto Retención Renta")
    isr_perceived_in_purchases = fields.Float("ISR Percibido en compras",
                                              help="Desabilitado")
    exicise_tax = fields.Float("Impuesto Selectivo al Consumo")
    other_tax_fees = fields.Float("Otros Impuesto/Tasas")
    legal_tip_amount = fields.Float("Monto Propina Legal")
    way_to_pay = fields.Selection(
        related='invoice_id.payment_ids.journal_id.payment_form',
        string="Forma de Pago")
