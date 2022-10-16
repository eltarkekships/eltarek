from odoo import SUPERUSER_ID, _, api, fields, models, tools


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_journal_income = fields.Boolean(default=False, compute='_compute_is_journal_income')

    @api.depends('account_id')
    def _compute_is_journal_income(self):
        for line in self:
            if line.account_id:
                # print('user_type_id', line.user_type_id)
                # print('user_type_id', line.user_type_id.name)
                if line.account_id.user_type_id.internal_group in ['income', 'expense']:
                    line.is_journal_income = True
                else:
                    print('no income')
                    line.is_journal_income = False
