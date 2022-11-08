from odoo import api, fields, models
from odoo.exceptions import UserError


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.constrains('price_unit')
    def check_price_unit_constrains(self):
        if self.price_unit <= 0:
            raise UserError('Price unit must be greater than 0')
