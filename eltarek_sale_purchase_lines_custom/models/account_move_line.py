from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('price_unit')
    def check_price_unit_constrains(self):
        for rec in self:
            if rec.exclude_from_invoice_tab is False:
                if rec.price_unit <= 0:
                    raise UserError('Price unit must be greater than 0')
