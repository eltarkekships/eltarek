# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_ship_product = fields.Boolean(string="Ship Product")


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    ship_id = fields.Many2one(comodel_name="product.product", string="Ship", domain=[('is_ship_product', '=', True)])
    ship_price = fields.Float(string="Ship Price")

    def update_prices(self):
        total_component_price = sum(line.product_qty * line.product_id.lst_price for line in self.line_ids)
        for line in self.line_ids:
            line.price_unit = line.product_id.lst_price * self.ship_price / total_component_price

    @api.model
    def create(self, vals):
        res = super(PurchaseRequisition, self).create(vals)
        res.update_prices()
        return res

    def write(self, vals):
        res = super(PurchaseRequisition, self).write(vals)
        self.update_prices()
        return res
