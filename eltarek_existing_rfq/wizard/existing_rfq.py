from odoo import models, fields, api


class ExistingPurchaseOrder(models.TransientModel):
    _name = 'existing.purchase.order'

    def _default_purchase_request_id(self):
        return self.env.context.get('active_id')

    def purchase_line_domain(self):
        for wizard in self:
            purchase_request = self.env['centione.purchase.request'].browse(self.env.context.get('active_id'))
            purchase_request_lines = purchase_request.purchase_lines_ids
            return [('id', 'in', purchase_request_lines.ids)]

    purchase_request_id = fields.Integer(default=_default_purchase_request_id)
    purchase_order_ids = fields.Many2many("purchase.order", string='Purchase Orders')
    wizard_line_ids = fields.Many2many('centione.purchase.request.line', string='Purchase Lines',
                                       domain=lambda self: [('request_id', '=', self.env.context.get('active_id'))])

    def add_to_existing_po(self):
        print('hi')
        for wizard in self:
            purchase_request = self.env['centione.purchase.request'].browse(wizard.purchase_request_id)
            for order in wizard.purchase_order_ids:
                order.purchase_request_ids = [(4, purchase_request.id)]
                for line in wizard.wizard_line_ids:
                    purchase_order_line = self.env['purchase.order.line']
                    purchase_order_line.create({
                                    'product_id': line.product_id.id,
                                    'name': line.product_id.name,
                                    'date_planned': fields.Datetime.now(),
                                    'product_uom': line.uom_id.id,
                                    'price_unit': 0.01,
                                    'product_qty': line.qty,
                                    'order_id': order.id,
                                })

                purchase_request.purchase_order_ids = [(4, order.id)]