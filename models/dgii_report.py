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
# ######################################################################.

"""

"""
import calendar
import base64
import string
import xlsxwriter
from datetime import datetime as dt

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class DgiiReportSaleSummary(models.Model):
    _name = 'dgii.reports.sale.summary'
    _order = 'sequence'

    name = fields.Char()
    sequence = fields.Integer()
    qty = fields.Integer()
    amount = fields.Monetary()
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    dgii_report_id = fields.Many2one('dgii.reports', ondelete='cascade')


class DgiiReport(models.Model):
    _name = 'dgii.reports'
    _inherit = ['mail.thread']

    name = fields.Char(string='Period', required=True, size=7)
    state = fields.Selection([('draft', 'New'), ('error', 'With error'),
                              ('generated', 'Generated'), ('sent', 'Sent')],
                             default='draft', track_visibility='onchange', copy=False)
    previous_balance = fields.Float('Previous balance', copy=False)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True,
                                  default=lambda self: self.env.user.company_id.currency_id)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id,
                                 required=True)

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name, company_id)', _("You cannot have more than one report by period."))
    ]

    @api.multi
    def _compute_606_fields(self):
        for rec in self:
            purchase_line_ids = self.env['dgii.reports.purchase.line'].search([('dgii_report_id', '=', rec.id)])
            x_1 = []
            x_2 = []
            x_3 = []
            x_4 = []
            x_5 = []
            x_6 = []
            x_7 = []
            x_8 = []
            x_9 = []
            x_10 = []
            x_11 = []
            x_12 = []
            for inv in purchase_line_ids:
                x_1.append(inv.service_total_amount)
                x_2.append(inv.good_total_amount)
                x_3.append(inv.invoiced_amount)
                x_4.append(inv.invoiced_itbis)
                x_5.append(inv.withholded_itbis)
                x_6.append(inv.proportionality_tax)
                x_7.append(inv.cost_itbis)
                x_8.append(inv.advance_itbis)
                x_9.append(inv.income_withholding)
                x_10.append(inv.selective_tax)
                x_11.append(inv.other_taxes)
                x_12.append(inv.legal_tip)

            rec.purchase_records = len(purchase_line_ids)
            rec.service_total_amount = abs(sum(x_1))
            rec.good_total_amount = abs(sum(x_2))
            rec.purchase_invoiced_amount = abs(sum(x_3))
            rec.purchase_invoiced_itbis = abs(sum(x_4))
            rec.purchase_withholded_itbis = abs(sum(x_5))
            rec.proportionality_tax = abs(sum(x_6))
            rec.cost_itbis = abs(sum(x_7))
            rec.advance_itbis = abs(sum(x_8))
            rec.income_withholding = abs(sum(x_9))
            rec.purchase_selective_tax = abs(sum(x_10))
            rec.purchase_other_taxes = abs(sum(x_11))
            rec.purchase_legal_tip = abs(sum(x_12))

    @api.multi
    def _compute_607_fields(self):
        for rec in self:
            sale_line_ids = self.env['dgii.reports.sale.line'].search([('dgii_report_id', '=', rec.id)])
            rec.sale_records = len(sale_line_ids)
            x_1 = []
            x_2 = []
            x_3 = []
            x_4 = []
            x_5 = []
            x_6 = []
            x_7 = []
            for inv in sale_line_ids:
                x_1.append(inv.invoiced_amount)
                x_2.append(inv.invoiced_itbis)
                x_3.append(inv.third_withheld_itbis)
                x_4.append(inv.third_income_withholding)
                x_5.append(inv.selective_tax)
                x_6.append(inv.other_taxes)
                x_7.append(inv.legal_tip)
            rec.sale_invoiced_amount = abs(sum(x_1))
            rec.sale_invoiced_itbis = abs(sum(x_2))
            rec.sale_withholded_itbis = abs(sum(x_3))
            rec.sale_withholded_isr = abs(sum(x_4))
            rec.sale_selective_tax = abs(sum(x_5))
            rec.sale_other_taxes = abs(sum(x_6))
            rec.sale_legal_tip = abs(sum(x_7))

    @api.multi
    def _compute_608_fields(self):
        for rec in self:
            cancel_line_ids = self.env['dgii.reports.cancel.line'].search([('dgii_report_id', '=', rec.id)])
            rec.cancel_records = len(cancel_line_ids)

    @api.multi
    def _compute_609_fields(self):
        for rec in self:
            external_line_ids = self.env['dgii.reports.exterior.line'].search([('dgii_report_id', '=', rec.id)])
            rec.exterior_records = len(external_line_ids)
            rec.presumed_income = abs(sum([inv.presumed_income for inv in external_line_ids]))
            rec.exterior_withholded_isr = abs(sum([inv.withholded_isr for inv in external_line_ids]))
            rec.exterior_invoiced_amount = abs(sum([inv.invoiced_amount for inv in external_line_ids]))

    # 606
    purchase_ids = fields.One2many('dgii.reports.purchase.line', 'dgii_report_id')
    purchase_records = fields.Integer(compute='_compute_606_fields')
    service_total_amount = fields.Monetary(compute='_compute_606_fields')
    good_total_amount = fields.Monetary(compute='_compute_606_fields')
    purchase_invoiced_amount = fields.Monetary(compute='_compute_606_fields')
    purchase_invoiced_itbis = fields.Monetary(compute='_compute_606_fields')
    purchase_withholded_itbis = fields.Monetary(compute='_compute_606_fields')
    proportionality_tax = fields.Monetary(compute='_compute_606_fields')
    cost_itbis = fields.Monetary(compute='_compute_606_fields')
    advance_itbis = fields.Monetary(compute='_compute_606_fields')
    income_withholding = fields.Monetary(compute='_compute_606_fields')
    purchase_selective_tax = fields.Monetary(compute='_compute_606_fields')
    purchase_other_taxes = fields.Monetary(compute='_compute_606_fields')
    purchase_legal_tip = fields.Monetary(compute='_compute_606_fields')
    purchase_filename = fields.Char()
    purchase_filename_xlsx = fields.Char()
    purchase_binary = fields.Binary(string='606 Archivo TXT')
    purchase_binary_xlsx = fields.Binary(string='606 Archivo Excel')

    # 607
    sale_ids = fields.One2many('dgii.reports.sale.line', 'dgii_report_id')
    sale_records = fields.Integer(compute='_compute_607_fields')
    sale_invoiced_amount = fields.Float(compute='_compute_607_fields')
    sale_invoiced_itbis = fields.Float(compute='_compute_607_fields')
    sale_withholded_itbis = fields.Float(compute='_compute_607_fields')
    sale_withholded_isr = fields.Float(compute='_compute_607_fields')
    sale_selective_tax = fields.Float(compute='_compute_607_fields')
    sale_other_taxes = fields.Float(compute='_compute_607_fields')
    sale_legal_tip = fields.Float(compute='_compute_607_fields')
    sale_filename = fields.Char()
    sale_filename_xlsx = fields.Char()
    sale_binary = fields.Binary(string='607 Archivo TXT')
    sale_binary_xlsx = fields.Binary(string='607 Archivo Excel')

    # 608
    cancel_ids = fields.One2many('dgii.reports.cancel.line', 'dgii_report_id')
    cancel_records = fields.Integer(compute='_compute_608_fields')
    cancel_filename = fields.Char()
    cancel_filename_xlsx = fields.Char()
    cancel_binary = fields.Binary(string='608 Archivo TXT')
    cancel_binary_xlsx = fields.Binary(string='608 Archivo Excel')

    # 609
    exterior_ids = fields.One2many('dgii.reports.exterior.line', 'dgii_report_id')
    exterior_records = fields.Integer(compute='_compute_609_fields')
    presumed_income = fields.Float(compute='_compute_609_fields')
    exterior_withholded_isr = fields.Float(compute='_compute_609_fields')
    exterior_invoiced_amount = fields.Float(compute='_compute_609_fields')
    exterior_filename = fields.Char()
    exterior_filename_xlsx = fields.Char()
    exterior_binary = fields.Binary(string='609 Archivo TXT')
    exterior_binary_xlsx = fields.Binary(string='609 Archivo Excel')

    # Additional Info
    ncf_sale_summary_ids = fields.One2many('dgii.reports.sale.summary', 'dgii_report_id',
                                           string='Operations by NCF type', copy=False)
    cash = fields.Monetary('Cash', copy=False)
    bank = fields.Monetary('Check / Transfer / Deposit', copy=False)
    card = fields.Monetary('Credit Card / Debit Card', copy=False)
    credit = fields.Monetary('Credit', copy=False)
    bond = fields.Monetary('Gift certificates or vouchers', copy=False)
    swap = fields.Monetary('Swap', copy=False)
    others = fields.Monetary('Other Sale Forms', copy=False)
    sale_type_total = fields.Monetary('Total', copy=False)

    opr_income = fields.Monetary('Operations Income (No-Financial)', copy=False)
    fin_income = fields.Monetary('Financial Income', copy=False)
    ext_income = fields.Monetary('Extraordinary Income', copy=False)
    lea_income = fields.Monetary('Lease Income', copy=False)
    ast_income = fields.Monetary('Depreciable Assets Income', copy=False)
    otr_income = fields.Monetary('Others Income', copy=False)
    income_type_total = fields.Monetary('Total', copy=False)

    def _validate_date_format(self, date):
        """Validate date format <MM/YYYY>"""
        if date is not None:
            error = _('Error. Date format must be MM/YYYY')
            if len(date) == 7:
                try:
                    dt.strptime(date, '%m/%Y')
                except ValueError:
                    raise ValidationError(error)
            else:
                raise ValidationError(error)

    @api.model
    def create(self, vals):
        self._validate_date_format(vals.get('name'))

        return super(DgiiReport, self).create(vals)

    @api.multi
    def write(self, vals):
        self._validate_date_format(vals.get('name'))

        return super(DgiiReport, self).write(vals)

    @api.multi
    def unlink(self):
        """When report is deleted, set all implied invoices fiscal_status to False"""
        for report in self:
            PurchaseLine = self.env['dgii.reports.purchase.line']
            SaleLine = self.env['dgii.reports.sale.line']
            CancelLine = self.env['dgii.reports.cancel.line']
            ExteriorLine = self.env['dgii.reports.exterior.line']
            invoice_ids = PurchaseLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += SaleLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += CancelLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += ExteriorLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            for inv in invoice_ids:
                inv.fiscal_status = False
        return super(DgiiReport, self).unlink()

    def _get_pending_invoices(self):
        return self.env['account.invoice'].search([('fiscal_status', '=', 'normal'), ('state', '=', 'paid')])

    def _get_invoices(self, rec):
        """
        Given rec and state, return a recordset of invoices
        :param rec: dgii.reports object
        :return: filtered invoices
        """
        month, year = rec.name.split('/')
        last_day = calendar.monthrange(int(year), int(month))[1]
        start_date = '{}-{}-01'.format(year, month)
        end_date = '{}-{}-{}'.format(year, month, last_day)

        invoice_ids = self.env['account.invoice'].search(
            [('date_invoice', '>=', start_date),
             ('date_invoice', '<=', end_date),
             ('company_id', '=', self.company_id.id)],
            order='date_invoice asc').filtered(lambda inv: (inv.journal_id.purchase_type != 'others') or
                                                           (inv.journal_id.ncf_control is True))

        # Append pending invoces (fiscal_status = Partial, state = Paid)
        invoice_ids += self._get_pending_invoices()

        return invoice_ids

    def formated_rnc_cedula(self, vat):
        if vat:
            if len(vat) in [9, 11]:
                id_type = 1 if len(vat) == 9 else 2
                return (vat.strip().replace('-', ''), id_type) if not vat.isspace() else False
            else:
                return False
        else:
            return False

    def _get_formated_date(self, date):

        return dt.strptime(date, '%Y-%m-%d').strftime('%Y%m%d') if date else ""

    def _get_formated_amount(self, amount):

        return str('{:.2f}'.format(abs(amount))).ljust(12)

    def process_606_report_data(self, values):

        pipe = '|'

        RNC = str(values['rnc_cedula'] if values['rnc_cedula'] else "")
        ID_TYPE = str(values['identification_type'] if values['identification_type'] else "").ljust(1)
        EXP_TYPE = str(values['expense_type'] if values['expense_type'] else "").ljust(2)
        NCF = str(values['fiscal_invoice_number']).ljust(11)
        NCM = str(values['modified_invoice_number'] if values['modified_invoice_number'] else "").ljust(19)
        INV_DATE = str(self._get_formated_date(values['invoice_date'])).ljust(8)
        PAY_DATE = str(self._get_formated_date(values['payment_date'])).ljust(8)
        SERV_AMOUNT = self._get_formated_amount(values['service_total_amount'])
        GOOD_AMOUNT = self._get_formated_amount(values['good_total_amount'])
        INV_AMOUNT = self._get_formated_amount(values['invoiced_amount'])
        INV_ITBIS = self._get_formated_amount(values['invoiced_itbis'])
        WH_ITBIS = self._get_formated_amount(values['withholded_itbis'])
        PROP_ITBIS = self._get_formated_amount(values['proportionality_tax'])
        COST_ITBIS = self._get_formated_amount(values['cost_itbis'])
        ADV_ITBIS = self._get_formated_amount(values['advance_itbis'])
        PP_ITBIS = ''
        WH_TYPE = str(values['isr_withholding_type'] if values['isr_withholding_type'] else "")
        INC_WH = self._get_formated_amount(values['income_withholding'])
        PP_ISR = ''
        ISC = self._get_formated_amount(values['selective_tax'])
        OTHR = self._get_formated_amount(values['other_taxes'])
        LEG_TIP = self._get_formated_amount(values['legal_tip'])
        PAY_FORM = str(values['payment_type'] if values['payment_type'] else "").ljust(2)

        return RNC + pipe + ID_TYPE + pipe + EXP_TYPE + pipe + NCF + pipe + NCM + pipe + INV_DATE + pipe + PAY_DATE + \
               pipe + SERV_AMOUNT + pipe + GOOD_AMOUNT + pipe + INV_AMOUNT + pipe + INV_ITBIS + pipe + WH_ITBIS + pipe \
               + PROP_ITBIS + pipe + COST_ITBIS + pipe + ADV_ITBIS + pipe + PP_ITBIS + pipe + WH_TYPE + pipe + INC_WH \
               + pipe + PP_ISR + pipe + ISC + pipe + OTHR + pipe + LEG_TIP + pipe + PAY_FORM

    def _generate_606_txt(self, report, records, qty):

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')

        header = "606|{}|{}|{}".format(str(company_vat).ljust(11), period, qty) + '\n'
        data = header + records

        file_path = '/tmp/DGII_606_{}_{}.txt'.format(company_vat, period)
        with open(file_path, 'w', encoding="utf-8", newline='\r\n') as txt_606:
            txt_606.write(str(data))

        report.write({
            'purchase_filename': file_path.replace('/tmp/', ''),
            'purchase_binary': base64.b64encode(open(file_path, 'rb').read())
        })

    def _generate_606_exlsx(self, report, records):
        list_header = [u'RNC o Cédula',
                       u'Tipo Id',
                       u'Tipo Bienes y Servicios Comprados',
                       u'NCF',
                       u'NCF ó Documento Modificado',
                       u'Fecha Comprobante',
                       u'DIA',
                       u'Fecha Pago',
                       u'DIA',
                       u'Monto Facturado en Servicios',
                       u'Monto Facturado en Bienes',
                       u'Total Monto Facturado',
                       u'ITBIS Facturado',
                       u'ITBIS Retenido',
                       u'ITBIS sujeto a Proporcionalidad (Art. 349)',
                       u'ITBIS llevado al Costo',
                       u'ITBIS por Adelantar',
                       u'ITBIS percibido en compras',
                       u'Tipo de Retención en ISR',
                       u'Monto Retención Renta',
                       u'ISR Percibido en compras',
                       u'Impuesto Selectivo al Consumo',
                       u'Otros Impuesto/Tasas',
                       u'Monto Propina Legal',
                       u'Forma de Pago']

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')
        # Create a workbook and add a worksheet.
        file_path = '/tmp/DGII_606_{}_{}.xlsx'.format(company_vat, period)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})

        alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

        for cell, header in zip(alphabet, list_header):
            worksheet.write(str(cell), str(header), bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        report.write({
            'purchase_filename_xlsx': file_path.replace('/tmp/', ''),
            'purchase_binary_xlsx': base64.b64encode(open(file_path, 'rb').read())
        })

    @api.multi
    def _compute_606_data(self, invoice_ids):

        def _prepare_list_for_xlsx(vals):
            def get_expense_type(val):
                key_sel = {
                    '01': '01-GASTOS DE PERSONAL',
                    '02': '02-GASTOS POR TABAJOS, SUMINISTROS Y SERVICIOS',
                    '03': '03-ARRENDAMIENTOS',
                    '04': '04-GASTOS DE ACTIVOS FIJOS',
                    '05': '05-GASTOS DE REPRESENTACION',
                    '06': '06-OTRAS DEDUCCIONES ADMITIDAS',
                    '07': '07-GASTOS FINANCIEROS',
                    '08': '08-GASTOS EXTRAORDINARIOS',
                    '09': '09-COMPRAS Y GRASTOS QUE FORMAN PARTE DEL COSTO DE VENTA',
                    '10': '10-ADQUISICIONES DE ACTIVOS',
                    '11': '11-GASTOS DE SEGUROS',
                }
                return key_sel.get(str(val), '')

            def get_format_date(val):
                return (dt.strptime(val, '%Y-%m-%d').strftime('%Y%m') if val else "",
                        dt.strptime(val, '%Y-%m-%d').strftime('%d') if val else "")

            def get_payment_type(val):
                key_sel = {
                    '01': '01-EFECTIVO',
                    '02': '02-CHEQUES/TRANSFERENCIAS/DEPOSITO',
                    '03': '03-TARJETA CREDITO/DEBITO',
                    '04': '04-COMPRA A CREDITO',
                    '05': '05-PERMUTA',
                    '06': '06-NOTA DE CREDITO',
                    '07': '07-MIXTO',
                }
                return key_sel.get(str(val), '04')

            def get_isr_withholding_type(val):
                key_sel = {
                    '01': '01-ALQUILERES',
                    '02': '02-HONORARIOS POR SERVICIOS',
                    '03': '03-OTRAS RENTAS',
                    '04': '04-OTRAS RENTAS (Rentas Presuntas)',
                    '05': '05-INTERESES PAGADOS A PERSONAS JURIDICAS RESIDENTES',
                    '06': '06-INTERESES PAGADOS A PERSONAS FISICAS RESIDENTES',
                    '07': '07-RETENCION POR PROVEEDORES DEL ESTADO',
                    '08': '08-JUEGOS TELEFONICOS',
                }
                return key_sel.get(str(val), '')

            inv_date, inv_day = get_format_date(vals['invoice_date'])
            pay_date, pay_day = get_format_date(vals['payment_date'])

            list_detail = [vals['rnc_cedula'] or '',
                           vals['identification_type'] or '',
                           get_expense_type(vals['expense_type']),
                           vals['fiscal_invoice_number'] or '',
                           vals['modified_invoice_number'] or '',
                           inv_date,
                           inv_day,
                           pay_date,
                           pay_day,
                           vals['service_total_amount'] or '',
                           vals['good_total_amount'] or '',
                           vals['invoiced_amount'] or '',
                           vals['invoiced_itbis'] or '',
                           vals['withholded_itbis'] or '',
                           vals['proportionality_tax'] or '',
                           vals['cost_itbis'] or '',
                           vals['advance_itbis'] or '',
                           vals['purchase_perceived_itbis'] or '',
                           vals['purchase_perceived_isr'] or '',
                           get_isr_withholding_type(vals['isr_withholding_type']),
                           vals['income_withholding'] or '',
                           vals['selective_tax'] or '',
                           vals['other_taxes'] or '',
                           vals['legal_tip'] or '',
                           get_payment_type(vals['payment_type']),
                           ]
            return list_detail

        for rec in self:
            PurchaseLine = self.env['dgii.reports.purchase.line']
            PurchaseLine.search([('dgii_report_id', '=', rec.id)]).unlink()

            line = 0
            report_data = ''
            report_list_for_xlsx = []
            for inv in invoice_ids:
                inv.fiscal_status = 'blocked'
                line += 1
                rnc_ced = self.formated_rnc_cedula(inv.partner_id.vat)
                values = {
                    'dgii_report_id': rec.id,
                    'line': line,
                    'rnc_cedula': rnc_ced[0] if rnc_ced else False,
                    'identification_type': rnc_ced[1] if rnc_ced else False,
                    'expense_type': inv.expense_type if inv.expense_type else False,
                    'fiscal_invoice_number': inv.reference,  # inv.reference,
                    'modified_invoice_number': inv.origin_out,
                    'invoice_date': inv.date_invoice,
                    'payment_date': inv.payment_date,
                    'service_total_amount': inv.service_total_amount,
                    'good_total_amount': inv.good_total_amount,
                    'invoiced_amount': inv.amount_untaxed_signed,
                    'invoiced_itbis': inv.invoiced_itbis,
                    'withholded_itbis': inv.withholded_itbis if inv.state == 'paid' else 0,
                    'proportionality_tax': inv.proportionality_tax,
                    'cost_itbis': inv.cost_itbis,
                    'advance_itbis': inv.advance_itbis,
                    'purchase_perceived_itbis': 0,  # Falta computarlo en la factura
                    'purchase_perceived_isr': 0,  # Falta computarlo en la factura
                    'isr_withholding_type': inv.isr_withholding_type,
                    'income_withholding': inv.income_withholding if inv.state == 'paid' else 0,
                    'selective_tax': inv.selective_tax,
                    'other_taxes': inv.other_taxes,
                    'legal_tip': inv.legal_tip,
                    'payment_type': inv.payment_form,
                    'invoice_partner_id': inv.partner_id.id,
                    'invoice_id': inv.id,
                    'credit_note': True if inv.type == 'in_refund' else False
                }
                PurchaseLine.create(values)
                report_data += self.process_606_report_data(values) + '\n'
                report_list_for_xlsx.append(_prepare_list_for_xlsx(values))
            self._generate_606_txt(rec, report_data, line)
            self._generate_606_exlsx(rec, report_list_for_xlsx)

    def _get_payments_dict(self):
        return {'cash': 0, 'bank': 0, 'card': 0, 'credit': 0, 'swap': 0, 'bond': 0, 'others': 0}

    def _convert_to_user_currency(self, base_currency, amount):
        context = dict(self._context or {})
        user_currency_id = self.env.user.company_id.currency_id
        base_currency_id = base_currency
        ctx = context.copy()
        return base_currency_id.with_context(ctx).compute(amount, user_currency_id)

    def _get_sale_payments_forms(self, invoice_id):
        payments_dict = self._get_payments_dict()
        Invoice = self.env['account.invoice']
        Payment = self.env['account.payment']

        if invoice_id.type == 'out_invoice':
            for payment in Invoice._get_invoice_payment_widget(invoice_id):
                payment_id = Payment.browse(payment['account_payment_id'])
                if payment_id:
                    key = payment_id.journal_id.payment_form
                    if key:
                        payments_dict[key] += self._convert_to_user_currency(invoice_id.currency_id, payment['amount'])
                else:
                    # If invoices is paid, but has not payment_id, assume it is a credit note
                    payments_dict['swap'] += self._convert_to_user_currency(invoice_id.currency_id, payment['amount'])
            payments_dict['credit'] += self._convert_to_user_currency(invoice_id.currency_id, invoice_id.residual)
        else:
            cn_payments = Invoice._get_invoice_payment_widget(invoice_id)
            for p in cn_payments:
                payments_dict['swap'] += self._convert_to_user_currency(invoice_id.currency_id, p['amount'])

            payments_dict['credit'] += self._convert_to_user_currency(invoice_id.currency_id, invoice_id.residual)

        return payments_dict

    def _get_607_operations_dict(self):
        return {
            'fiscal': {'sequence': 1, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTE VÁLIDO PARA CRÉDITO FISCAL',
                       'dgii_report_id': self.id},
            'final': {'sequence': 2, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTE CONSUMIDOR FINAL',
                      'dgii_report_id': self.id},
            'nd': {'sequence': 3, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTES NOTA DE DÉBITO',
                   'dgii_report_id': self.id},
            'nc': {'sequence': 4, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTES NOTA DE CRÉDITO',
                   'dgii_report_id': self.id},
            'unico': {'sequence': 5, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTE REGISTRO ÚNICO DE INGRESOS',
                      'dgii_report_id': self.id},
            'special': {'sequence': 6, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTE REGISTRO REGIMENES ESPECIALES',
                        'dgii_report_id': self.id},
            'gov': {'sequence': 7, 'qty': 0, 'amount': 0, 'name': 'COMPROBANTES GUBERNAMENTALES',
                    'dgii_report_id': self.id},
            'positive': {'sequence': 8, 'qty': 0, 'amount': 0, 'name': 'OTRAS OPERACIONES (POSITIVAS)',
                         'dgii_report_id': self.id},
            'negative': {'sequence': 9, 'qty': 0, 'amount': 0, 'name': 'OTRAS OPERACIONES (NEGATIVAS)',
                         'dgii_report_id': self.id},
        }

    def _process_op_dict(self, dict, invoice):
        op_dict = dict
        if invoice.sale_fiscal_type and invoice.type != 'out_refund':
            op_dict[invoice.sale_fiscal_type]['qty'] += 1
            op_dict[invoice.sale_fiscal_type]['amount'] += invoice.amount_untaxed_signed
        if invoice.type == 'out_refund' and not invoice.is_nd:
            op_dict['nc']['qty'] += 1
            op_dict['nc']['amount'] += invoice.amount_untaxed_signed
        if invoice.is_nd:
            op_dict['nd']['qty'] += 1
            op_dict['nd']['amount'] += invoice.amount_untaxed_signed

        return op_dict

    @api.multi
    def _set_payment_form_fields(self, payments_dict):
        for rec in self:
            rec.cash = payments_dict.get('cash')
            rec.bank = payments_dict.get('bank')
            rec.card = payments_dict.get('card')
            rec.credit = payments_dict.get('credit')
            rec.bond = payments_dict.get('bond')
            rec.swap = payments_dict.get('swap')
            rec.others = payments_dict.get('others')
            rec.sale_type_total = rec.cash + rec.bank + \
                                  rec.card + rec.credit + \
                                  rec.bond + rec.swap + rec.others

    def _get_income_type_dict(self):
        return {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0}

    def _process_income_dict(self, dict, invoice):
        income_dict = dict
        if invoice.income_type:
            income_dict[invoice.income_type] += invoice.amount_untaxed_signed
        return income_dict

    @api.multi
    def _set_income_type_fields(self, income_dict):
        for rec in self:
            rec.opr_income = income_dict.get('01')
            rec.fin_income = income_dict.get('02')
            rec.ext_income = income_dict.get('03')
            rec.lea_income = income_dict.get('04')
            rec.ast_income = income_dict.get('05')
            rec.otr_income = income_dict.get('06')
            rec.income_type_total = rec.opr_income + rec.fin_income + rec.ext_income + \
                                    rec.lea_income + rec.ast_income + rec.otr_income

    def process_607_report_data(self, values):

        pipe = '|'

        RNC = str(values['rnc_cedula'] if values['rnc_cedula'] else "").ljust(11)
        ID_TYPE = str(values['identification_type'] if values['identification_type'] else "")
        NCF = str(values['fiscal_invoice_number']).ljust(11)
        NCM = str(values['modified_invoice_number'] if values['modified_invoice_number'] else "").ljust(19)
        INCOME_TYPE = str(values['income_type']).ljust(2)
        INV_DATE = str(self._get_formated_date(values['invoice_date'])).ljust(8)
        WH_DATE = str(self._get_formated_date(values['withholding_date'])).ljust(8)
        INV_AMOUNT = self._get_formated_amount(values['invoiced_amount'])
        INV_ITBIS = self._get_formated_amount(values['invoiced_itbis'])
        WH_ITBIS = self._get_formated_amount(values['third_withheld_itbis'])
        PRC_ITBIS = ''
        WH_ISR = self._get_formated_amount(values['third_income_withholding'])
        PCR_ISR = ''
        ISC = self._get_formated_amount(values['selective_tax'])
        OTH_TAX = self._get_formated_amount(values['other_taxes'])
        LEG_TIP = self._get_formated_amount(values['legal_tip'])
        CASH = self._get_formated_amount(values['cash'])
        BANK = self._get_formated_amount(values['bank'])
        CARD = self._get_formated_amount(values['card'])
        CRED = self._get_formated_amount(values['credit'])
        SWAP = self._get_formated_amount(values['swap'])
        BOND = self._get_formated_amount(values['bond'])
        OTHR = self._get_formated_amount(values['others'])

        return RNC + pipe + ID_TYPE + pipe + NCF + pipe + NCM + pipe + INCOME_TYPE + pipe + \
               INV_DATE + pipe + WH_DATE + pipe + INV_AMOUNT + pipe + INV_ITBIS + pipe + \
               WH_ITBIS + pipe + PRC_ITBIS + pipe + WH_ISR + pipe + PCR_ISR + pipe + ISC + pipe + OTH_TAX + pipe + \
               LEG_TIP + pipe + CASH + pipe + BANK + pipe + CARD + pipe + CRED + pipe + SWAP + pipe + BOND + pipe + OTHR

    def _generate_607_txt(self, report, records, qty):

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')

        header = "607|{}|{}|{}".format(str(company_vat).ljust(11), period, qty) + '\n'
        data = header + records

        file_path = '/tmp/DGII_607_{}_{}.txt'.format(company_vat, period)
        with open(file_path, 'w', encoding="utf-8", newline='\r\n') as txt_607:
            txt_607.write(str(data))

        report.write({
            'sale_filename': file_path.replace('/tmp/', ''),
            'sale_binary': base64.b64encode(open(file_path, 'rb').read())
        })

    def _generate_607_exlsx(self, report, records):
        list_header = [u'RNC/Cédula o Pasaporte',
                       u'Tipo Identificación',
                       u'Número Comprobante Fiscal',
                       u'Número Comprobante Fiscal Modificado',
                       u'Tipo de Ingreso',
                       u'Fecha Comprobante',
                       u'Fecha de Retención',
                       u'Monto Facturado',
                       u'ITBIS Facturado',
                       u'ITBIS Retenido por Terceros',
                       u'ITBIS Percibido',
                       u'Retención Renta por Terceros',
                       u'ISR Percibido',
                       u'Impuesto Selectivo al Consumo',
                       u'Otros Impuestos/Tasas',
                       u'Monto Propina Legal',
                       u'Efectivo',
                       u'Cheque/ Transferencia/ Depósito',
                       u'Tarjeta Débito/Crédito',
                       u'Venta a Crédito',
                       u'Bonos o Certificados de Regalo',
                       u'Permuta',
                       u'Otras Formas de Ventas']

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')
        # Create a workbook and add a worksheet.
        file_path = '/tmp/DGII_607_{}_{}.xlsx'.format(company_vat, period)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})
        # List the alphabet
        alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

        for cell, header in zip(alphabet, list_header):
            worksheet.write(str(cell), str(header), bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        report.write({
            'sale_filename_xlsx': file_path.replace('/tmp/', ''),
            'sale_binary_xlsx': base64.b64encode(open(file_path, 'rb').read())
        })

    @api.multi
    def _compute_607_data(self, invoice_ids):
        def _prepare_list_for_xlsx(vals):

            inv_date = self._get_formated_date(values['invoice_date'])
            withholding_date = self._get_formated_date(vals['withholding_date'])

            list_detail = [vals['rnc_cedula'] or '',
                           vals['identification_type'] or '',
                           vals['fiscal_invoice_number'] or '',
                           vals['modified_invoice_number'] or '',
                           vals['income_type'] or '',
                           inv_date,
                           withholding_date,
                           vals['invoiced_amount'] or '',
                           vals['invoiced_itbis'] or '',
                           vals['third_withheld_itbis'] or '',
                           vals['perceived_itbis'] or '',
                           vals['third_income_withholding'] or '',
                           vals['perceived_isr'] or '',
                           vals['selective_tax'] or '',
                           vals['other_taxes'] or '',
                           vals['legal_tip'],
                           vals['cash'],
                           vals['bank'],
                           vals['card'],
                           vals['credit'],
                           vals['swap'],
                           vals['bond'],
                           vals['others'],
                           ]
            return list_detail

        for rec in self:
            SaleLine = self.env['dgii.reports.sale.line']
            SaleLine.search([('dgii_report_id', '=', rec.id)]).unlink()

            # invoice_ids = self._get_invoices(rec, ['open', 'paid'], ['out_invoice', 'out_refund'])
            line = 0
            op_dict = self._get_607_operations_dict()
            payment_dict = self._get_payments_dict()
            income_dict = self._get_income_type_dict()

            report_data = ''
            report_list_for_xlsx = []
            for inv in invoice_ids:
                op_dict = self._process_op_dict(op_dict, inv)
                income_dict = self._process_income_dict(income_dict, inv)
                inv.fiscal_status = 'blocked'
                rnc_ced = self.formated_rnc_cedula(inv.partner_id.vat)
                payments = self._get_sale_payments_forms(inv)
                values = {
                    'dgii_report_id': rec.id,
                    'line': line,
                    'rnc_cedula': rnc_ced[0] if rnc_ced else False,
                    'identification_type': rnc_ced[1] if rnc_ced else False,
                    'fiscal_invoice_number': inv.reference,
                    'modified_invoice_number': inv.origin_out if inv.origin_out and inv.origin_out[-10:-8] in ['01',
                                                                                                               '02',
                                                                                                               '14',
                                                                                                               '15'] else False,
                    'income_type': inv.income_type,
                    'invoice_date': inv.date_invoice,
                    'withholding_date': inv.payment_date if (inv.type != 'out_refund' and any(
                        [inv.withholded_itbis, inv.income_withholding])) else False,
                    'invoiced_amount': inv.amount_untaxed_signed,
                    'invoiced_itbis': inv.invoiced_itbis,
                    'third_withheld_itbis': inv.third_withheld_itbis if inv.state == 'paid' else 0,
                    'perceived_itbis': 0,  # Pendiente
                    'third_income_withholding': inv.third_income_withholding if inv.state == 'paid' else 0,
                    'perceived_isr': 0,  # Pendiente
                    'selective_tax': inv.selective_tax,
                    'other_taxes': inv.other_taxes,
                    'legal_tip': inv.legal_tip,
                    'invoice_partner_id': inv.partner_id.id,
                    'invoice_id': inv.id,
                    'credit_note': True if inv.type == 'out_refund' else False,
                    'cash': payments.get('cash'),
                    'bank': payments.get('bank'),
                    'card': payments.get('card'),
                    'credit': payments.get('credit'),
                    'swap': payments.get('swap'),
                    'bond': payments.get('bond'),
                    'others': payments.get('others')
                }

                if str(values.get('fiscal_invoice_number'))[-10:-8] == '02' and inv.amount_untaxed_signed < 250000:
                    # Excluye las facturas de Consumo con monto menor a 250000
                    pass
                else:
                    line += 1
                    values.update({'line': line})
                    SaleLine.create(values)
                    report_data += self.process_607_report_data(values) + '\n'
                    report_list_for_xlsx.append(_prepare_list_for_xlsx(values))

                for k in payment_dict:
                    if inv.type != 'out_refund':
                        payment_dict[k] += payments[k]

            for k in op_dict:
                self.env['dgii.reports.sale.summary'].create(op_dict[k])

            self._set_payment_form_fields(payment_dict)
            self._set_income_type_fields(income_dict)
            self._generate_607_txt(rec, report_data, line)
            self._generate_607_exlsx(rec, report_list_for_xlsx)

    def process_608_report_data(self, values):

        pipe = '|'

        NCF = str(values['fiscal_invoice_number']).ljust(11)
        INV_DATE = str(self._get_formated_date(values['invoice_date'])).ljust(8)
        ANU_TYPE = str(values['anulation_type']).ljust(2)

        return NCF + pipe + INV_DATE + pipe + ANU_TYPE

    def _generate_608_txt(self, report, records, qty):

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')

        header = "608|{}|{}|{}".format(str(company_vat).ljust(11), period, qty) + '\n'
        data = header + records

        file_path = '/tmp/DGII_608_{}_{}.txt'.format(company_vat, period)
        with open(file_path, 'w', encoding="utf-8", newline='\r\n') as txt_608:
            txt_608.write(str(data))

        report.write({
            'cancel_filename': file_path.replace('/tmp/', ''),
            'cancel_binary': base64.b64encode(open(file_path, 'rb').read())
        })

    def _generate_608_exlsx(self, report, records):
        list_header = [u'Número Comprobante Fiscal',
                       u'Fecha Comprobante',
                       u'Tipo de Anulación']

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')
        # Create a workbook and add a worksheet.
        file_path = '/tmp/DGII_608_{}_{}.xlsx'.format(company_vat, period)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})
        # List the alphabet
        alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

        for cell, header in zip(alphabet, list_header):
            worksheet.write(str(cell), str(header), bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        report.write({
            'cancel_filename_xlsx': file_path.replace('/tmp/', ''),
            'cancel_binary_xlsx': base64.b64encode(open(file_path, 'rb').read())
        })

    @api.multi
    def _compute_608_data(self, invoice_ids):
        def _prepare_list_for_xlsx(vals):
            def get_anulation_type(val):
                key_sel = {
                    '01': '01 Deterioro de Factura Pre-impresa',
                    '02': u'02 Errores de Impresión (Factura Pre-impresa)',
                    '03': u'03 Impresión Defectuosa',
                    '04': u'04 Corrección de la Información',
                    '05': '05 Cambio de Productos',
                    '06': u'06 Devolución de Productos',
                    '07': u'07 Omisión de Productos',
                    '08': '08 Errores en Secuencia de NCF',
                    '09': '09 Por Cese de Operaciones',
                    '10': '10 Pérdida o Hurto de Talonarios',
                }
                return key_sel.get(str(val), '04')

            inv_date = self._get_formated_date(values['invoice_date'])

            list_detail = [vals['fiscal_invoice_number'] or '',
                           inv_date,
                           get_anulation_type(vals['anulation_type']),
                           ]
            return list_detail

        for rec in self:
            CancelLine = self.env['dgii.reports.cancel.line']
            CancelLine.search([('dgii_report_id', '=', rec.id)]).unlink()

            # invoice_ids = self._get_invoices(rec, ['cancel'], ['out_invoice', 'out_refund'])
            line = 0
            report_data = ''
            report_list_for_xlsx = []
            for inv in invoice_ids:
                inv.fiscal_status = 'blocked'
                line += 1
                values = {
                    'dgii_report_id': rec.id,
                    'line': line,
                    'invoice_partner_id': inv.partner_id.id,
                    'fiscal_invoice_number': inv.reference,
                    'invoice_date': inv.date_invoice,
                    'anulation_type': inv.anulation_type,
                    'invoice_id': inv.id
                }
                CancelLine.create(values)
                report_data += self.process_608_report_data(values) + '\n'
                report_list_for_xlsx.append(_prepare_list_for_xlsx(values))

            self._generate_608_txt(rec, report_data, line)
            self._generate_608_exlsx(rec, report_list_for_xlsx)

    def process_609_report_data(self, values):

        pipe = '|'

        LEGAL_NAME = str(values['legal_name']).ljust(50)
        # ID_TYPE = str(values['tax_id_type'] if values['identification_type'] else "")
        ID_TYPE = str(values['tax_id_type'] or "")
        TAX_ID = str(values['tax_id'] if values['tax_id'] else "").ljust(50)
        CNT_CODE = str(values['country_code'] if values['country_code'] else "").ljust(3)
        PST = str(values['purchased_service_type'] if values['purchased_service_type'] else "").ljust(2)
        STD = str(values['service_type_detail'] if values['service_type_detail'] else "").ljust(2)
        REL_PART = str(values['related_part'] if values['related_part'] else "").ljust(1)
        DOC_NUM = str(values['doc_number'] if values['doc_number'] else "").ljust(30)
        DOC_DATE = str(self._get_formated_date(values['doc_date'])).ljust(8)
        INV_AMOUNT = self._get_formated_amount(values['invoiced_amount'])
        ISR_DATE = str(self._get_formated_date(values['isr_withholding_date'])).ljust(8)
        PRM_INCM = self._get_formated_amount(values['presumed_income'])
        WH_ISR = self._get_formated_amount(values['withholded_isr'])

        return LEGAL_NAME + pipe + ID_TYPE + pipe + TAX_ID + pipe + CNT_CODE + pipe + PST + pipe + STD + pipe + \
               REL_PART + pipe + DOC_NUM + pipe + DOC_DATE + pipe + INV_AMOUNT + pipe + ISR_DATE + pipe + PRM_INCM + \
               pipe + WH_ISR

    def _generate_609_txt(self, report, records, qty):

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')

        header = "609|{}|{}|{}".format(str(company_vat).ljust(11), period, qty) + '\n'
        data = header + records

        file_path = '/tmp/DGII_609_{}_{}.txt'.format(company_vat, period)
        with open(file_path, 'w', encoding="utf-8", newline='\r\n') as txt_609:
            txt_609.write(str(data))

        report.write({
            'exterior_filename': file_path.replace('/tmp/', ''),
            'exterior_binary': base64.b64encode(open(file_path, 'rb').read())
        })

    def _generate_609_exlsx(self, report, records):
        list_header = [u'Nombre / Razón Social',
                       u'Tipo ID Tributación',
                       u'ID Tributaria',
                       u'País De Destino',
                       u'Tipo De Servicio Adquirido',
                       u'Detalle del Servicio Adquirido',
                       u'Parte Relacionada',
                       u'Número De Documento',
                       u'Fecha De Documento',
                       u'Monto Facturado',
                       u'Fecha de Retención',
                       u'Renta Presunta',
                       u'ISR Retenido',
                       ]

        company_vat = report.company_id.vat
        period = dt.strptime(report.name.replace('/', ''), '%m%Y').strftime('%Y%m')
        # Create a workbook and add a worksheet.
        file_path = '/tmp/DGII_609_{}_{}.xlsx'.format(company_vat, period)
        workbook = xlsxwriter.Workbook(file_path, {'strings_to_numbers': True})
        worksheet = workbook.add_worksheet()
        # Add a bold format to use to highlight cells.
        bold = workbook.add_format({'bold': 1})
        # List the alphabet
        alphabet = ["%s%d" % (l, 1) for l in string.ascii_uppercase]

        for cell, header in zip(alphabet, list_header):
            worksheet.write(str(cell), str(header), bold)

        row = 1
        for rec in records:
            for col, detail in enumerate(rec):
                worksheet.write(row, col, detail)
            row += 1

        workbook.close()

        report.write({
            'exterior_filename_xlsx': file_path.replace('/tmp/', ''),
            'exterior_binary_xlsx': base64.b64encode(open(file_path, 'rb').read())
        })

    @api.multi
    def _compute_609_data(self, invoice_ids):
        def _prepare_list_for_xlsx(vals):

            DOC_DATE = str(self._get_formated_date(values['doc_date'])).ljust(8)
            INV_AMOUNT = self._get_formated_amount(values['invoiced_amount'])
            ISR_DATE = str(self._get_formated_date(values['isr_withholding_date'])).ljust(8)
            PRM_INCM = self._get_formated_amount(values['presumed_income'])
            WH_ISR = self._get_formated_amount(values['withholded_isr'])

            list_detail = [vals['legal_name'] or '',
                           vals['tax_id_type'] or '',
                           vals['tax_id'] or '',
                           vals['country_code'] or '',
                           vals['purchased_service_type'] or '',
                           vals['service_type_detail'] or '',
                           vals['related_part'] or '',
                           vals['doc_number'] or '',
                           DOC_DATE,
                           INV_AMOUNT,
                           ISR_DATE,
                           PRM_INCM,
                           WH_ISR,

                           ]
            return list_detail

        for rec in self:
            ExteriorLine = self.env['dgii.reports.exterior.line']
            ExteriorLine.search([('dgii_report_id', '=', rec.id)]).unlink()

            line = 0
            report_data = ''
            report_list_for_xlsx = []
            for inv in invoice_ids:
                inv.fiscal_status = 'blocked'
                line += 1
                values = {
                    'dgii_report_id': rec.id,
                    'line': line,
                    'legal_name': inv.partner_id.name,
                    'tax_id_type': 1 if inv.partner_id.company_type == 'individual' else 2,
                    'tax_id': inv.partner_id.vat,
                    'country_code': inv.partner_id.country_id.code,
                    'purchased_service_type': inv.service_type,
                    'service_type_detail': inv.service_type_detail.code,
                    'related_part': int(inv.partner_id.related),
                    'doc_number': inv.name,
                    'doc_date': inv.date_invoice,
                    'invoiced_amount': inv.amount_untaxed_signed,
                    'isr_withholding_date': inv.payment_date,
                    'presumed_income': 0,  # Pendiente
                    'withholded_isr': inv.income_withholding if inv.state == 'paid' else 0,
                    'invoice_id': inv.id
                }
                ExteriorLine.create(values)
                report_data += self.process_609_report_data(values) + '\n'
                report_list_for_xlsx.append(_prepare_list_for_xlsx(values))

            self._generate_609_txt(rec, report_data, line)
            self._generate_609_exlsx(rec, report_list_for_xlsx)

    @api.multi
    def generate_report(self):
        # Drop 607 NCF Operations for recompute
        # Filter Applied to know where is belong to.
        self.env['dgii.reports.sale.summary'].search([('dgii_report_id', '=', self.id)]).unlink()
        invoices = self._get_invoices(rec=self)
        self._compute_606_data(invoice_ids=list(
            filter(lambda r: r.state in ['open', 'paid'] and
                             r.journal_id.purchase_type in ['normal', 'minor', 'informal'] and
                             r.type in ['in_invoice', 'in_refund'], invoices)))
        self._compute_607_data(invoice_ids=list(
            filter(lambda r: r.state in ['open', 'paid'] and r.type in ['out_invoice', 'out_refund'], invoices)))
        self._compute_608_data(invoice_ids=list(
            filter(lambda r: r.state in ['cancel'] and r.type in ['out_invoice', 'out_refund'], invoices)))
        self._compute_609_data(invoice_ids=list(
            filter(lambda r: r.state in ['open', 'paid'] and
                             r.type in ['in_invoice', 'in_refund'] and
                             r.partner_id.country_id.code != 'DO' and
                             r.journal_id.purchase_type == 'exterior'
                   , invoices)))
        self.state = 'generated'

    def _has_withholding(self, inv):
        """Validate if given invoice has an Withholding tax"""
        return True if any([inv.income_withholding,
                            inv.withholded_itbis,
                            inv.third_withheld_itbis,
                            inv.third_income_withholding]) else False

    @api.multi
    def _invoice_status_sent(self):
        for report in self:
            PurchaseLine = self.env['dgii.reports.purchase.line']
            SaleLine = self.env['dgii.reports.sale.line']
            CancelLine = self.env['dgii.reports.cancel.line']
            ExteriorLine = self.env['dgii.reports.exterior.line']
            invoice_ids = PurchaseLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += SaleLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += CancelLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            invoice_ids += ExteriorLine.search([('dgii_report_id', '=', report.id)]).mapped('invoice_id')
            for inv in invoice_ids:
                if inv.state in ['paid', 'cancel']:
                    inv.fiscal_status = 'done'
                    continue

                if self._has_withholding(inv):
                    inv.fiscal_status = 'normal'
                else:
                    inv.fiscal_status = 'done'

    @api.multi
    def state_sent(self):
        for report in self:
            self._invoice_status_sent()
            report.state = 'sent'

    def get_606_tree_view(self):
        return {
            'name': '606',
            'view_mode': 'tree',
            'res_model': 'dgii.reports.purchase.line',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ncf_dgii_reports.dgii_report_purchase_line_tree').id,
            'domain': [('dgii_report_id', '=', self.id)]
        }

    def get_607_tree_view(self):
        return {
            'name': '607',
            'view_mode': 'tree',
            'res_model': 'dgii.reports.sale.line',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ncf_dgii_reports.dgii_report_sale_line_tree').id,
            'domain': [('dgii_report_id', '=', self.id)]
        }

    def get_608_tree_view(self):
        return {
            'name': '608',
            'view_mode': 'tree',
            'res_model': 'dgii.reports.cancel.line',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ncf_dgii_reports.dgii_cancel_report_line_tree').id,
            'domain': [('dgii_report_id', '=', self.id)]
        }

    def get_609_tree_view(self):
        return {
            'name': '609',
            'view_mode': 'tree',
            'res_model': 'dgii.reports.exterior.line',
            'type': 'ir.actions.act_window',
            'view_id': self.env.ref('ncf_dgii_reports.dgii_exterior_report_line_tree').id,
            'domain': [('dgii_report_id', '=', self.id)]
        }


class DgiiReportPurchaseLine(models.Model):
    _name = 'dgii.reports.purchase.line'
    _order = 'line asc'

    dgii_report_id = fields.Many2one('dgii.reports', ondelete='cascade')
    line = fields.Integer()

    rnc_cedula = fields.Char(size=11)
    identification_type = fields.Char(size=1)
    expense_type = fields.Char(size=2)
    fiscal_invoice_number = fields.Char(size=19)
    modified_invoice_number = fields.Char(size=19)
    invoice_date = fields.Date()
    payment_date = fields.Date()
    service_total_amount = fields.Float()
    good_total_amount = fields.Float()
    invoiced_amount = fields.Float()
    invoiced_itbis = fields.Float()
    withholded_itbis = fields.Float()
    proportionality_tax = fields.Float()
    cost_itbis = fields.Float()
    advance_itbis = fields.Float()
    purchase_perceived_itbis = fields.Float()
    isr_withholding_type = fields.Char()
    income_withholding = fields.Float()
    purchase_perceived_isr = fields.Float()
    selective_tax = fields.Float()
    other_taxes = fields.Float()
    legal_tip = fields.Float()
    payment_type = fields.Char()

    invoice_partner_id = fields.Many2one('res.partner')
    invoice_id = fields.Many2one('account.invoice')
    credit_note = fields.Boolean()


class DgiiReportSaleLine(models.Model):
    _name = 'dgii.reports.sale.line'

    dgii_report_id = fields.Many2one('dgii.reports', ondelete='cascade')
    line = fields.Integer()

    rnc_cedula = fields.Char(size=11)
    identification_type = fields.Char(size=1)
    fiscal_invoice_number = fields.Char(size=19)
    modified_invoice_number = fields.Char(size=19)
    income_type = fields.Char()
    invoice_date = fields.Date()
    withholding_date = fields.Date()
    invoiced_amount = fields.Float()
    invoiced_itbis = fields.Float()
    third_withheld_itbis = fields.Float()
    perceived_itbis = fields.Float()
    third_income_withholding = fields.Float()
    perceived_isr = fields.Float()
    selective_tax = fields.Float()
    other_taxes = fields.Float()
    legal_tip = fields.Float()

    # Tipo de Venta/ Forma de pago
    cash = fields.Float()
    bank = fields.Float()
    card = fields.Float()
    credit = fields.Float()
    bond = fields.Float()
    swap = fields.Float()
    others = fields.Float()

    invoice_partner_id = fields.Many2one('res.partner')
    invoice_id = fields.Many2one('account.invoice')
    credit_note = fields.Boolean()


class DgiiCancelReportLine(models.Model):
    _name = 'dgii.reports.cancel.line'

    dgii_report_id = fields.Many2one('dgii.reports', ondelete='cascade')
    line = fields.Integer()

    fiscal_invoice_number = fields.Char(size=19)
    invoice_date = fields.Date()
    anulation_type = fields.Char(size=2)

    invoice_partner_id = fields.Many2one('res.partner')
    invoice_id = fields.Many2one('account.invoice')


class DgiiExteriorReportLine(models.Model):
    _name = 'dgii.reports.exterior.line'

    dgii_report_id = fields.Many2one('dgii.reports', ondelete='cascade')
    line = fields.Integer()

    legal_name = fields.Char()
    tax_id_type = fields.Integer()
    tax_id = fields.Char()
    country_code = fields.Char()
    purchased_service_type = fields.Char(size=2)
    service_type_detail = fields.Char(size=2)
    related_part = fields.Integer()
    doc_number = fields.Char()
    doc_date = fields.Date()
    invoiced_amount = fields.Float()
    isr_withholding_date = fields.Date()
    presumed_income = fields.Float()
    withholded_isr = fields.Float()
    invoice_id = fields.Many2one('account.invoice')
