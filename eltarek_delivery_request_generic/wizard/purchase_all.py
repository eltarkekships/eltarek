from odoo import api, fields, models, _


class PurchaseAllRequest(models.TransientModel):
    _name = 'purchase.all.wizard'
    _description = 'Purchase All Wizard'

    delivery_id = fields.Many2one(comodel_name="centione.delivery.request")
    line_ids = fields.One2many("purchase.all.wizard.line", 'transfer_id')
    request_lines = fields.Many2many('centione.delivery.request.line')

    @api.onchange('line_ids')
    def onchange_line_ids(self):
        print('hi')
        for rec in self:
            return {'domain': {'line_ids': [('line_id', 'in', rec.delivery_id.delivery_lines_ids.ids)]}}



    def confirm_purchasing(self):
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
                line.create_or_modify_line('normal')
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
    _name = 'purchase.all.wizard.line'

    transfer_id = fields.Many2one(comodel_name="purchase.all.wizard")
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

    def create_or_modify_line(self, line_type):
        # delivery_request = self.env['centione.delivery.request'].browse(self.env.context.get('active_id'))
        delivery_request_line = self.env['centione.delivery.request.line'].browse(self.line_id.id)
        # purchase_request = self.env['centione.purchase.request'].search([('state', '=', 'open')], limit=1)
        purchase_request = self.env['centione.purchase.request'].search([('delivery_request_id', '=', delivery_request_line.request_id.id)], limit=1)
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
                                         'qty': self.transfer_quantity,
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
                    purchase_line.qty += self.transfer_quantity
                    return {}
            # if there wasn't any open lines, create new one
            # delivery_request_line.requested_amount += self.requested_amount
            delivery_request_line.requested_amount = self.transfer_quantity
            request_line_values = {
                'product_id': delivery_request_line.product_id.id,
                'cost_price': delivery_request_line.product_id.standard_price,
                # 'qty': delivery_request_line.qty,
                'qty': self.transfer_quantity,
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
            # context.update({'employee_used_case': self.employee.work_email})
            # template = self.env.ref('eltarek_delivery_request_generic.mail_purchase_request_created_notification')
            # template.with_context(context).sudo().send_mail(purchase_request.id, force_send=True)
            return True