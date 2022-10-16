# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    product_department_ids = fields.Many2many('hr.department', string='Department')
    picking_type_first_id = fields.Many2one(comodel_name="stock.picking.type", string="First Picking Type",
                                            required=False, )
    picking_type_second_id = fields.Many2one(comodel_name="stock.picking.type", string="Second Picking Type",
                                             required=False, )
    picking_type_purchase_id = fields.Many2one(comodel_name="stock.picking.type", string="Purchase Picking Type",
                                               required=False, )
    delivery_location_id = fields.Many2one('stock.location', string='Source Location')
    delivery_location_dest_id = fields.Many2one('stock.location', string='Destination Location')
