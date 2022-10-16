# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategoryInherit(models.Model):
    _inherit = "product.category"

    manager_id = fields.Many2many('res.users', string='Manager')
    picking_type_first_id = fields.Many2one(comodel_name="stock.picking.type", string="First Picking Type",
                                            required=False, )
    picking_type_second_id = fields.Many2one(comodel_name="stock.picking.type", string="Second Picking Type",
                                             required=False, )
    picking_type_purchase_id = fields.Many2one(comodel_name="stock.picking.type", string="Purchase Picking Type",
                                               required=False, )
    delivery_location_id = fields.Many2one('stock.location', string='Source Location')
    delivery_location_dest_id = fields.Many2one('stock.location', string='Destination Location')
