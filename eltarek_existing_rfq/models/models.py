# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CentionePurchaseRequestInherit(models.Model):
    _inherit = 'centione.purchase.request'

    purchase_order_ids = fields.Many2many('purchase.order')

    def request_orders_action(self):
        return {
            'name': 'Purchase Orders',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain': [('purchase_request_ids', '=', self.id)],
        }

    smart_button_request = fields.Integer(compute='compute_request')

    def compute_request(self):
        for rec in self:
            self.smart_button_request = len(rec.env['purchase.order'].search([('purchase_request_ids', '=', rec.id)]))


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def request_orders_action(self):
        return {
            'name': 'Purchase Requests',
            'view_mode': 'tree,form',
            'res_model': 'centione.purchase.request',
            'type': 'ir.actions.act_window',
            'domain': [('purchase_order_ids', '=', self.id)],
        }

    smart_button_request = fields.Integer(compute='compute_request')

    def compute_request(self):
        for rec in self:
            self.smart_button_request = len(rec.env['centione.purchase.request'].search([('purchase_order_ids', '=', rec.id)]))

