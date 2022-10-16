from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class TransferAllRequest(models.TransientModel):
    _name = 'transfer.all.wizard'
    _description = 'Transfer All Wizard'

    delivery_id = fields.Many2one(comodel_name="centione.delivery.request")
    line_ids = fields.One2many("transfer.all.wizard.line", 'transfer_id')
    request_lines = fields.Many2many('centione.delivery.request.line')

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        print('hi')
        for rec in self:
            return {'domain': {'line_ids': [('line_id', 'in', rec.delivery_id.delivery_lines_ids.ids)]}}


    def confirm_transferring(self):
        for rec in self:
            move_lines = []
            location_id = rec.line_ids[0].line_id.product_id.categ_id.delivery_location_id.id
            location_dest_id = rec.line_ids[0].line_id.product_id.categ_id.delivery_location_dest_id.id
            picking_type_id = rec.line_ids[0].line_id.product_id.categ_id.picking_type_first_id.id
            origin = rec.line_ids[0].line_id.request_id.name
            analytic_account_id = rec.line_ids[0].line_id.request_id.analytic_account_id.id
            delivery_request_line_id = rec.line_ids[0].line_id.id
            for line in rec.line_ids:
                delivery_request_line = line.line_id
                if picking_type_id:
                    # delivery_request_line.requested_amount += self.requested_amount
                    delivery_request_line.requested_amount += line.transfer_quantity
                    move_lines.append([0, False, {
                            # 'date_expected': fields.Datetime.now(),
                            'product_uom': delivery_request_line.uom_id.id,
                            'product_id': delivery_request_line.product_id.id,
                            'name': delivery_request_line.product_id.name,
                            'picking_type_id': picking_type_id,
                            # 'product_uom_qty': delivery_request_line.qty,
                            'product_uom_qty': line.transfer_quantity,
                            'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                            'state': 'draft'
                        }])
                delivery_request_line.broker_warehouse = delivery_request_line.product_id.categ_id.delivery_location_dest_id.id
                if delivery_request_line.qty == delivery_request_line.requested_amount:
                    delivery_request_line.state = 'requested'
            values = {
                'location_id': location_id,
                'location_dest_id': location_dest_id,
                'move_type': 'one',
                'picking_type_id': picking_type_id,
                'picking_type_code': 'internal',
                'priority': '1',
                'state': 'draft',
                'origin': origin,
                # 'min_date': fields.Datetime.now(),
                'name': '/',
                'analytic_account_id': analytic_account_id,
                'delivery_request_line_id': delivery_request_line_id,
                'move_lines': move_lines
            }
            picking = self.env['stock.picking'].create(values)
            picking.action_confirm()
            return True
                # else:
                #     raise ValidationError("There Is No 'Picking Type' Assigned To The Warehouse Of Source Location")


class TransferAllRequestLine(models.TransientModel):
    _name = 'transfer.all.wizard.line'

    transfer_id = fields.Many2one(comodel_name="transfer.all.wizard")
    delivery_id = fields.Many2one(comodel_name="centione.delivery.request", related='transfer_id.delivery_id')

    # @api.onchange('line_id')
    # def onchange_line(self):
    #     self.ensure_one()
    #     self.context()
            # return {'domain': {'line_id': [('request_id', '=', rec.delivery_id.id)]}}

    # def _get_domain(self):
    #     ids = []
    #     for line in self.transfer_id.delivery_id.delivery_lines_ids:
    #         print('hhhhhhhhhh')
    #         ids.append(line.id)
    #     return [('id', 'in', ids)]

    transfer_quantity = fields.Float(string="Requested Amount")
    line_id = fields.Many2one(comodel_name="centione.delivery.request.line",)
                              # domain=_get_domain)
