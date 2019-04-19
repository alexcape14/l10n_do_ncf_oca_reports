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
Reporte de cancelacion 608 para la de dgii
"""
import logging

from odoo import fields, models, api

from .tools import gen_years, gen_months, TODAY

_logger = logging.getLogger(__name__)


class DgiiReport608(models.Model):
    _name = 'dgii.report.608'
    _description = "Reporte de cancelacion 608 para la dgii"

    company_id = fields.Many2one(
            comodel_name='res.company',
            string='Empresa',
            default=lambda self:
            self.env['res.company']._company_default_get('dgii.report.608'),
            required=True)
    report_608_line = fields.One2many('report.608.line', 'dgii_report_608_id')
    count_register = fields.Integer('Cantidad de Registros')
    rnc_or_schedule = fields.Char('RNC',
                                  size=11,
                                  related='company_id.partner_id.vat',
                                  required=True)
    year = fields.Selection(gen_years, required=True, index=True,
                            default=lambda self: str(TODAY.year))
    month = fields.Selection(gen_months, required=True, index=True,
                             default=lambda self: TODAY.month - 1, store=True)
    state = fields.Selection(
            [('draft', 'Nuevo'),
             ('error', 'Con errores'),
             ('done', 'Valido')], default='draft')

    @api.multi
    @api.depends('report_608_line')
    def _compute_count_register(self):
        _logger.info("compute count register 608")
        for rec in self:
            rec.count_register = rec.report_608_line and \
                    len(rec.report_608_line)


class Report608Line(models.Model):
    _name = 'report.608.line'
    _description = "Lineas eportes de ventas DGII 608"

    line = fields.Integer("Linea")
    dgii_report_608_id = fields.Many2one('dgii.report.608')
    invoice_id = fields.Many2one('account.invoice', 'NCF')
    is_credit_note = fields.Boolean()

    rnc_or_schedule = fields.Char("RNC", size=11,
                                  related='invoice_id.partner_id.vat')
    identification_type = fields.Char("Tipo ID", size=1)
