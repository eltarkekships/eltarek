# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountAnalyticAccountInherit(models.Model):
    _inherit = 'account.analytic.account'
    location_id = fields.Many2one('stock.location', "Location")


class AccountAccountInherit(models.Model):
    _inherit = 'account.account'

    with_analytic = fields.Boolean("Analytic")
