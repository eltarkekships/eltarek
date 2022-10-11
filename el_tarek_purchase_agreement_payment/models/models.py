# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    def action_payment(self):
        return {
            'name': _('Register Payment'),
            'res_model': 'account.payment',
            'view_mode': 'form',
            'context': {
                'default_payment_type': 'outbound',
                'default_partner_type': 'supplier',
                'default_move_journal_types': ('bank', 'cash'),
                'default_partner_id': self.vendor_id.id,
                # 'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


class Payment(models.Model):
    _inherit = 'account.payment'

    # def get_guarantee_account_domain(self):
    #     return [('user_type_id', '!=', self.env.ref('account.data_account_type_liquidity').id)]

    guarantee_account_id = fields.Many2one('account.account', 'Account')
    is_guarantee = fields.Boolean(string="Destination Account")

    @api.depends('journal_id', 'partner_id', 'partner_type', 'is_internal_transfer', 'guarantee_account_id',
                 'is_guarantee')
    def _compute_destination_account_id(self):
        self.destination_account_id = False
        for pay in self:
            if pay.is_internal_transfer:
                pay.destination_account_id = pay.journal_id.company_id.transfer_account_id
            else:
                if pay.guarantee_account_id and pay.is_guarantee:
                    pay.destination_account_id = pay.guarantee_account_id
                    print(pay.destination_account_id.name)
                elif pay.partner_type == 'customer':
                    # Receive money from invoice or send money to refund it.
                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(
                            pay.company_id).property_account_receivable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('internal_type', '=', 'receivable'),
                            ('deprecated', '=', False),
                        ], limit=1)
                elif pay.partner_type == 'supplier':
                    # Send money to pay a bill or receive money to refund it.

                    if pay.partner_id:
                        pay.destination_account_id = pay.partner_id.with_company(pay.company_id).property_account_payable_id
                    else:
                        pay.destination_account_id = self.env['account.account'].search([
                            ('company_id', '=', pay.company_id.id),
                            ('internal_type', '=', 'payable'),
                            ('deprecated', '=', False),
                        ], limit=1)

    def _synchronize_from_moves(self, changed_fields):
        ''' Update the account.payment regarding its related account.move.
        Also, check both models are still consistent.
        :param changed_fields: A set containing all modified fields on account.move.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):

            # After the migration to 14.0, the journal entry could be shared between the account.payment and the
            # account.bank.statement.line. In that case, the synchronization will only be made with the statement line.
            if pay.move_id.statement_line_id:
                continue

            move = pay.move_id
            move_vals_to_write = {}
            payment_vals_to_write = {}

            if 'journal_id' in changed_fields:
                if pay.journal_id.type not in ('bank', 'cash'):
                    raise UserError(_("A payment must always belongs to a bank or cash journal."))

            if 'line_ids' in changed_fields:
                all_lines = move.line_ids
                liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

                if len(liquidity_lines) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one outstanding payments/receipts account.",
                        move.display_name,
                    ))

                if len(counterpart_lines) != 1 and not self.is_guarantee:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "include one and only one receivable/payable account (with an exception of "
                        "internal transfers).",
                        move.display_name,
                    ))

                if writeoff_lines and len(writeoff_lines.account_id) != 1:
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, "
                        "all optional journal items must share the same account.",
                        move.display_name,
                    ))

                if any(line.currency_id != all_lines[0].currency_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same currency.",
                        move.display_name,
                    ))

                if any(line.partner_id != all_lines[0].partner_id for line in all_lines):
                    raise UserError(_(
                        "Journal Entry %s is not valid. In order to proceed, the journal items must "
                        "share the same partner.",
                        move.display_name,
                    ))

                if counterpart_lines.account_id.user_type_id.type == 'receivable':
                    partner_type = 'customer'
                else:
                    partner_type = 'supplier'

                liquidity_amount = liquidity_lines.amount_currency

                move_vals_to_write.update({
                    'currency_id': liquidity_lines.currency_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                payment_vals_to_write.update({
                    'amount': abs(liquidity_amount),
                    'partner_type': partner_type,
                    'currency_id': liquidity_lines.currency_id.id,
                    'destination_account_id': counterpart_lines.account_id.id,
                    'partner_id': liquidity_lines.partner_id.id,
                })
                if liquidity_amount > 0.0:
                    payment_vals_to_write.update({'payment_type': 'inbound'})
                elif liquidity_amount < 0.0:
                    payment_vals_to_write.update({'payment_type': 'outbound'})

            move.write(move._cleanup_write_orm_values(move, move_vals_to_write))
            pay.write(move._cleanup_write_orm_values(pay, payment_vals_to_write))

    def _synchronize_to_moves(self, changed_fields):
        ''' Update the account.move regarding the modified account.payment.
        :param changed_fields: A list containing all modified fields on account.payment.
        '''
        if self._context.get('skip_account_move_synchronization'):
            return

        if not any(field_name in changed_fields for field_name in (
            'date', 'amount', 'payment_type', 'partner_type', 'payment_reference', 'is_internal_transfer',
            'currency_id', 'partner_id', 'destination_account_id', 'partner_bank_id', 'guarantee_account_id'
        )):
            return

        for pay in self.with_context(skip_account_move_synchronization=True):
            liquidity_lines, counterpart_lines, writeoff_lines = pay._seek_for_lines()

            # Make sure to preserve the write-off amount.
            # This allows to create a new payment with custom 'line_ids'.

            if writeoff_lines:
                counterpart_amount = sum(counterpart_lines.mapped('amount_currency'))
                writeoff_amount = sum(writeoff_lines.mapped('amount_currency'))

                # To be consistent with the payment_difference made in account.payment.register,
                # 'writeoff_amount' needs to be signed regarding the 'amount' field before the write.
                # Since the write is already done at this point, we need to base the computation on accounting values.
                if (counterpart_amount > 0.0) == (writeoff_amount > 0.0):
                    sign = -1
                else:
                    sign = 1
                writeoff_amount = abs(writeoff_amount) * sign

                write_off_line_vals = {
                    'name': writeoff_lines[0].name,
                    'amount': writeoff_amount,
                    'account_id': writeoff_lines[0].account_id.id,
                }
            else:
                write_off_line_vals = {}

            line_vals_list = pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)

            line_ids_commands = [
                (1, liquidity_lines.id, line_vals_list[0]),
                (1, counterpart_lines.id, line_vals_list[1]),
            ]

            for line in writeoff_lines:
                line_ids_commands.append((2, line.id))

            for extra_line_vals in line_vals_list[2:]:
                line_ids_commands.append((0, 0, extra_line_vals))

            # Update the existing journal items.
            # If dealing with multiple write-off lines, they are dropped and a new one is generated.

            pay.move_id.write({
                'partner_id': pay.partner_id.id,
                'currency_id': pay.currency_id.id,
                'partner_bank_id': pay.partner_bank_id.id,
                'line_ids': line_ids_commands,
            })

    # @api.model_create_multi
    # def create(self, vals_list):
    #     # OVERRIDE
    #     write_off_line_vals_list = []
    #
    #     for vals in vals_list:
    #
    #         # Hack to add a custom write-off line.
    #         write_off_line_vals_list.append(vals.pop('write_off_line_vals', None))
    #
    #         # Force the move_type to avoid inconsistency with residual 'default_move_type' inside the context.
    #         vals['move_type'] = 'entry'
    #
    #         # Force the computation of 'journal_id' since this field is set on account.move but must have the
    #         # bank/cash type.
    #         if 'journal_id' not in vals:
    #             vals['journal_id'] = self._get_default_journal().id
    #
    #         # Since 'currency_id' is a computed editable field, it will be computed later.
    #         # Prevent the account.move to call the _get_default_currency method that could raise
    #         # the 'Please define an accounting miscellaneous journal in your company' error.
    #         if 'currency_id' not in vals:
    #             journal = self.env['account.journal'].browse(vals['journal_id'])
    #             vals['currency_id'] = journal.currency_id.id or journal.company_id.currency_id.id
    #
    #     payments = super().create(vals_list)
    #
    #     for i, pay in enumerate(payments):
    #         write_off_line_vals = write_off_line_vals_list[i]
    #
    #         # Write payment_id on the journal entry plus the fields being stored in both models but having the same
    #         # name, e.g. partner_bank_id. The ORM is currently not able to perform such synchronization and make things
    #         # more difficult by creating related fields on the fly to handle the _inherits.
    #         # Then, when partner_bank_id is in vals, the key is consumed by account.payment but is never written on
    #         # account.move.
    #         to_write = {'payment_id': pay.id}
    #         for k, v in vals_list[i].items():
    #             if k in self._fields and self._fields[k].store and k in pay.move_id._fields and pay.move_id._fields[
    #                 k].store:
    #                 to_write[k] = v
    #
    #         if 'line_ids' not in vals_list[i]:
    #             to_write['line_ids'] = [(0, 0, line_vals) for line_vals in
    #                                     pay._prepare_move_line_default_vals(write_off_line_vals=write_off_line_vals)]
    #
    #         pay.move_id.write(to_write)
    #
    #     return payments


