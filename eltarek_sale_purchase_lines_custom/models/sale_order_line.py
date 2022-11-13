from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('price_unit')
    def check_price_unit_constrains(self):
        for rec in self:
            if rec.price_unit <= 0:
                raise UserError('Price unit must be greater than 0')
