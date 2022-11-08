from odoo import api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.constrains('price_unit')
    def check_price_unit_constrains(self):
        if self.price_unit <= 0:
            raise UserError('Price unit must be greater than 0')
