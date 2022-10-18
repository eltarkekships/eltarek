from odoo import SUPERUSER_ID, _, api, fields, models, tools


class HrExpense(models.Model):
    _inherit = 'hr.expense'
    is_income = fields.Boolean(default=False, compute='_compute_is_income')

    @api.depends('account_id')
    def _compute_is_income(self):
        if self.account_id:
            if self.account_id.user_type_id.internal_group in ['income', 'expense']:
                self.is_income = True
            else:
                print('no income')
                self.is_income = False





class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_income = fields.Boolean(default=False, compute='_compute_is_income')
    # is_journal_income = fields.Boolean(default=False, compute='_compute_is_journal_income')

    # @api.depends('account_id')
    # def _compute_is_journal_income(self):
    #     for line in self:
    #         if line.account_id:
    #             # print('user_type_id', line.user_type_id)
    #             # print('user_type_id', line.user_type_id.name)
    #             if line.account_id.user_type_id.internal_group in ['income', 'expense']:
    #                 line.is_journal_income = True
    #             else:
    #                 print('no income')
    #                 line.is_journal_income = False

    @api.depends('account_id')
    def _compute_is_income(self):
        for line in self:
            if line.account_id:
                if line.account_id.user_type_id.internal_group in ['income', 'expense']:
                    line.is_income = True
                else:
                    print('no income')
                    line.is_income = False

