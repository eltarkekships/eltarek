# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import datetime


class CentioneProcessRequest(models.TransientModel):
    _name = 'centione.process.request'
    _description = 'Centione Process Delivery Request'

    location_id = fields.Many2one('stock.location', "Source Location", required=False)
    location_dest_id = fields.Many2one('stock.location', "Destination Location", required=False)
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse")
    employee = fields.Many2one('hr.employee')
    requested_amount = fields.Float(string="Requested Amount", required=False, )

    def create_centione_transfer(self):
        self.ensure_one()
        delivery_request_line = self.env['centione.delivery.request.line'].browse(self.env.context.get('active_id'))
        picking_type_id = delivery_request_line.product_id.categ_id.picking_type_first_id.id
        if picking_type_id:
            # delivery_request_line.requested_amount += self.requested_amount
            delivery_request_line.requested_amount = self.requested_amount
            values = {
                'location_id': delivery_request_line.product_id.categ_id.delivery_location_id.id,
                'location_dest_id': delivery_request_line.product_id.categ_id.delivery_location_dest_id.id,
                'move_type': 'one',
                'picking_type_id': picking_type_id,
                'picking_type_code': 'internal',
                'priority': '1',
                'state': 'draft',
                'origin': delivery_request_line.request_id.name,
                # 'min_date': fields.Datetime.now(),
                'name': '/',
                'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                'delivery_request_line_id': delivery_request_line.id,
                'move_lines': [[0, False, {
                    'location_id': delivery_request_line.product_id.categ_id.delivery_location_id.id,
                    'location_dest_id': delivery_request_line.product_id.categ_id.delivery_location_dest_id.id,

                    # 'date_expected': fields.Datetime.now(),
                    'product_uom': delivery_request_line.uom_id.id,
                    'product_id': delivery_request_line.product_id.id,
                    'name': delivery_request_line.product_id.name,
                    'picking_type_id': picking_type_id,
                    # 'product_uom_qty': delivery_request_line.qty,
                    'product_uom_qty': self.requested_amount,
                    'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                    'state': 'draft'
                }]]
            }
            picking = self.env['stock.picking'].create(values)
            picking.action_confirm()
            delivery_request_line.broker_warehouse = delivery_request_line.product_id.categ_id.delivery_location_dest_id.id
            if delivery_request_line.qty == delivery_request_line.requested_amount:
                delivery_request_line.state = 'requested'
            return True
        else:
            raise ValidationError("There Is No 'Picking Type' Assigned To The Warehouse Of Source Location")

    def create_centione_purchase(self):
        self.ensure_one()
        self.create_centione_transfer()
        self.create_or_modify_line('normal')
        return {}

    def create_or_modify_line(self, line_type):
        # delivery_request = self.env['centione.delivery.request'].browse(self.env.context.get('active_id'))
        delivery_request_line = self.env['centione.delivery.request.line'].browse(self.env.context.get('active_id'))
        # purchase_request = self.env['centione.purchase.request'].search([('state', '=', 'open')], limit=1)
        purchase_request = self.env['centione.purchase.request'].search(
            [('delivery_request_id', '=', delivery_request_line.request_id.id)], limit=1)
        # picking_type_id = int(self.env['ir.config_parameter'].sudo().get_param('picking_type_purchase_id')) or False
        picking_type_id = delivery_request_line.product_id.picking_type_purchase_id.id or False
        if not purchase_request:
            # delivery_request_line.requested_amount += self.requested_amount
            request_vals = {
                'origin': delivery_request_line.request_id.name,
                'delivery_request_id': delivery_request_line.request_id.id,
                'purchase_lines_ids': [[0, False,
                                        {'product_id': delivery_request_line.product_id.id,
                                         'cost_price': delivery_request_line.product_id.standard_price,
                                         'delivery_request_line_id': delivery_request_line.id,
                                         # 'qty': delivery_request_line.qty,
                                         'qty': self.requested_amount,
                                         'uom_id': delivery_request_line.uom_id.id,
                                         'state': 'draft',
                                         'type': line_type,
                                         'picking_type_id': picking_type_id,
                                         'notes': delivery_request_line.notes}]]
            }
            self.env['centione.purchase.request'].create(request_vals)
        else:
            # Check if there is already opened line for this product in the open purchase request lines
            for purchase_line in purchase_request.purchase_lines_ids:
                if purchase_line.product_id.id == delivery_request_line.product_id.id \
                        and purchase_line.type == line_type and purchase_line.state != 'done' \
                        and purchase_line.uom_id.id == delivery_request_line.uom_id.id \
                        and purchase_line.picking_type_id.id == picking_type_id:
                    # purchase_line.qty += delivery_request_line.qty
                    # delivery_request_line.requested_amount += self.requested_amount
                    purchase_line.qty += self.requested_amount
                    return {}
            # if there wasn't any open lines, create new one
            # delivery_request_line.requested_amount += self.requested_amount
            delivery_request_line.requested_amount = self.requested_amount
            request_line_values = {
                'product_id': delivery_request_line.product_id.id,
                'cost_price': delivery_request_line.product_id.standard_price,
                # 'qty': delivery_request_line.qty,
                'qty': self.requested_amount,
                'uom_id': delivery_request_line.uom_id.id,
                'state': 'draft',
                'notes': delivery_request_line.notes,
                'request_id': purchase_request.id,
                'type': line_type,
                'picking_type_id': picking_type_id
            }
            self.env['centione.purchase.request.line'].create(request_line_values)
            delivery_request_line.state = 'purchase_request'
            context = dict(self.env.context)
            context.update({'employee_used_case': self.employee.work_email})
            template = self.env.ref('eltarek_delivery_request_generic.mail_purchase_request_created_notification')
            template.with_context(context).sudo().send_mail(purchase_request.id, force_send=True)
            return True


class ReceiveConfirmation(models.TransientModel):
    _name = 'receive.confirmation'
    _description = 'Receive Confirmation'

    received_amount = fields.Float('Quantity')

    def confirm_transferring(self):
        self.ensure_one()
        delivery_request_line = self.env['centione.delivery.request.line'].browse(self.env.context.get('active_id'))
        if self.received_amount > delivery_request_line.qty:
            raise ValidationError(
                "Sorry, That Is Invalid Quantity : Received Quantity Cannot Exceed Requested Quantity")
        if not delivery_request_line.request_id.analytic_account_id.location_id:
            raise ValidationError("Sorry, There Is No Location Assigned To Analytic Account")

        picking_type = delivery_request_line.product_id.categ_id.picking_type_second_id.id
        # for pick in delivery_request_line.picking_ids:
        #     if pick.state != 'done':
        #         raise ValidationError(_('Not All Products Received From Stock'))
        if picking_type:
            total_recieved_amount = delivery_request_line.received_amount + self.received_amount
            if total_recieved_amount > delivery_request_line.qty:
                raise ValidationError(_('Received Qty Is Greater Than The Requested Qty'))
            delivery_request_line.received_amount = total_recieved_amount
            delivery_request_line.receive_line_function()
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
                'move_lines': [[0, False, {
                    # 'date_expected': fields.Datetime.now(),
                    'product_uom': delivery_request_line.uom_id.id,
                    'product_id': delivery_request_line.product_id.id,
                    'name': delivery_request_line.product_id.name,
                    'picking_type_id': picking_type,
                    'product_uom_qty': self.received_amount,
                    # 'ordered_qty': self.received_amount,
                    # 'qty_done': self.received_amount,
                    'analytic_account_id': delivery_request_line.request_id.analytic_account_id.id,
                    'quantity_done': self.received_amount,
                    'reserved_availability': self.received_amount,
                    'state': 'draft',
                    'location_id': delivery_request_line.broker_warehouse.id,
                    'location_dest_id': delivery_request_line.request_id.analytic_account_id.location_id.id,
                }]]
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
