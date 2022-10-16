from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ReceiveAllRequest(models.TransientModel):
    _name = 'receive.all.wizard'
    _description = 'receive All Wizard'

    delivery_id = fields.Many2one(comodel_name="centione.delivery.request")
    line_ids = fields.One2many("receive.all.wizard.line", 'receive_id')
    request_lines = fields.Many2many('centione.delivery.request.line')

    # @api.onchange('line_ids')
    # def onchange_line_ids(self):
    #     print('hi')
    #     for rec in self:
    #         return {'domain': {'line_ids': [('line_id', 'in', rec.delivery_id.delivery_lines_ids.ids)]}}


    def confirm_receiving(self):
        for rec in self:
            delivery_request_line = rec.line_ids[0].line_id

            if not delivery_request_line.request_id.analytic_account_id.location_id:
                raise ValidationError("Sorry, There Is No Location Assigned To Analytic Account")
            picking_type = delivery_request_line.product_id.categ_id.picking_type_second_id.id
            if picking_type:
                move_lines = []
                for line in rec.line_ids:
                    delivery_request_line = line.line_id
                    if line.received_amount > delivery_request_line.qty:
                        raise ValidationError(
                            "Sorry, That Is Invalid Quantity : Received Quantity Cannot Exceed Requested Quantity")
                    total_recieved_amount = delivery_request_line.received_amount + line.received_amount
                    if total_recieved_amount > delivery_request_line.qty:
                        raise ValidationError(_('Received Qty Is Greater Than The Requested Qty'))
                    delivery_request_line.received_amount = total_recieved_amount
                    delivery_request_line.receive_line_function()
                    move_lines.append([0, False, {
                        # 'date_expected': fields.Datetime.now(),
                        'product_uom': delivery_request_line.uom_id.id,
                        'product_id': delivery_request_line.product_id.id,
                        'name': delivery_request_line.product_id.name,
                        'picking_type_id': delivery_request_line.product_id.categ_id.picking_type_second_id.id,
                        'product_uom_qty': line.received_amount,
                        # 'ordered_qty': line.received_amount,
                        # 'qty_done': line.received_amount,
                        'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                        'quantity_done': line.received_amount,
                        'reserved_availability': line.received_amount,
                        'state': 'draft'
                    }])
                delivery_request_line = rec.line_ids[0].line_id
                values = {
                    'location_id': delivery_request_line.broker_warehouse.id,
                    'location_dest_id': delivery_request_line.request_id.analytic_account_id.location_id.id,
                    'move_type': 'one',
                    'picking_type_id': picking_type,
                    'priority': '1',
                    'state': 'draft',
                    'origin': delivery_request_line.request_id.name,
                    # 'min_date': fields.Datetime.now(),
                    'name': '/',
                    'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                    'move_lines': move_lines
                }
                picking = self.env['stock.picking'].create(values)
                # picking.action_confirm()
                # picking.force_assign()
                for move in picking.move_lines:
                    # move.qty_done = move.product_uom_qty
                    move.reserved_availability = move.product_uom_qty

                # picking.force_assign()
                # picking.do_new_transfer()
                picking.button_validate()
                # for rec in picking.move_ids_without_package:
                #     for account in rec.account_move_ids:
                #         for line in account.line_ids:
                #             if line.account_id.with_analytic:
                #                 line.analytic_account_id = delivery_request_line.request_id.analytic_account_id.id
                #         account.line_ids.create_analytic_lines()
                # picking.action_done()

                return True
            else:
                raise ValidationError(
                    "There Is No 'Picking Type' Assigned To The Warehouse Of Location Of Analytic Account")


class ReceiveAllRequestLine(models.TransientModel):
    _name = 'receive.all.wizard.line'

    receive_id = fields.Many2one(comodel_name="receive.all.wizard")
    delivery_id = fields.Many2one(comodel_name="centione.delivery.request", related='receive_id.delivery_id')

    # @api.onchange('line_id')
    # def onchange_line(self):
    #     self.ensure_one()
    #     self.context()
            # return {'domain': {'line_id': [('request_id', '=', rec.delivery_id.id)]}}

    # def _get_domain(self):
    #     ids = []
    #     for line in self.receive_id.delivery_id.delivery_lines_ids:
    #         print('hhhhhhhhhh')
    #         ids.append(line.id)
    #     return [('id', 'in', ids)]

    received_amount = fields.Float(string="Received Amount")
    line_id = fields.Many2one(comodel_name="centione.delivery.request.line",)
                              # domain=_get_domain)