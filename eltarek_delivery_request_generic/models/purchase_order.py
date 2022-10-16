from odoo import api, models, fields


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    purchase_request_ids = fields.Many2many(comodel_name="centione.purchase.request")
    delivery_request_line_id = fields.Integer()
    initial_mrp_line_id = fields.Integer()
