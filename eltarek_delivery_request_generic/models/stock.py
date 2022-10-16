# -*- coding: utf-8 -*-
from odoo import fields, models
from collections import defaultdict


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    delivery_request_line_id = fields.Many2one('centione.delivery.request.line', string="Delivery Request Line")


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        res = super(StockMoveInherit, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        # if self.picking_type_id.code == 'incoming':
        #     for line in res:
        #         if line[2]['debit'] > 0:
        #             line[2]['analytic_account_id'] = self.picking_id.analytic_account_id.id
        for line in res:
            # account = self.env['account.account'].browse(line[2]['account_id'])
            # if account.user_type_id.has_analytic_account:
            line[2]['analytic_account_id'] = self.picking_id.analytic_account_id.id
        return res

# class StockMoveLineInherit(models.Model):
#     _inherit = "stock.move.line"
#
#     analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account',related='picking_id.analytic_account_id')

