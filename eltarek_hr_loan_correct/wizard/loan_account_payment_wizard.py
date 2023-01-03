# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import logging
from datetime import datetime, timedelta, date

LOGGER = logging.getLogger(__name__)
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    loan_id = fields.Many2one('loan.payment', string="Loan")

class LoanAccountPaymentWizard(models.TransientModel):
    _name = 'loan.account.payment.wizard'

    payment_journal_id = fields.Many2one(comodel_name='account.journal', string='Payment Journal',
                                         domain='[("type","in",["bank","cash"])]',required=True)
    emp_account_id = fields.Many2one('account.account', string="Debit",required=True)
    treasury_account_id = fields.Many2one('account.account', string="Credit",required=True)

    def action_approve(self):
        for rec in self:
            loan_id = self.env.context.get('active_id')
            loan = self.env['loan.payment'].browse(loan_id)
            move_id = self.env['account.move'].create({
                'name': loan.name,
                'ref': loan.employee_id.hr_code,
                'date': loan.req_date,
                'journal_id': rec.payment_journal_id.id,
                # 'state': 'posted',
                'line_ids': [(0, 0, {
                    'name': loan.name,
                    'ref': loan.employee_id.name,
                    'account_id': rec.treasury_account_id.id,
                    'debit': 0.0,
                    'credit': loan.req_amount,
                    'journal_id': rec.payment_journal_id.id,
                    'company_id': self.env.user.company_id.id,
                    'amount_currency': 0.0,
                    'date_maturity': loan.req_date,
                    'loan_id': loan.id,
                }), (0, 0, {
                    'name': loan.name,
                    'ref': loan.employee_id.hr_code,
                    'account_id': rec.emp_account_id.id,
                    'credit': 0.0,
                    'debit': loan.req_amount,
                    'journal_id': rec.payment_journal_id.id,
                    'company_id': self.env.user.company_id.id,
                    'amount_currency': 0.0,
                    'date_maturity': loan.req_date,
                    'loan_id': loan.id,
                })]
            })
            move_id.action_post()
            loan.write({'move_id': move_id.id})


    def generate_payment(self):
        loan_id = self.env.context.get('active_id')
        loan = self.env['loan.payment'].browse(loan_id)
        acc_payment_date = 'Loan/' + datetime.now().strftime("%Y") + '/' + loan.name
        vals = {
            'payment_type': 'outbound',
            'partner_type': 'customer',
            'partner_id': loan.partner_id.id,
            'amount': loan.req_amount,
            'journal_id': self.payment_journal_id.id,
            # 'communication': loan.desc,
            'payment_method_id': self.env.ref('account.account_payment_method_manual_out').id,
            'source_doc': acc_payment_date
        }
        loan.state = 'closed'
        # self.env['account.payment'].create(vals)
        payment_loan = self.env['hr.loan'].search([('name','=',loan.desc),('employee_id','=',loan.employee_id.id)])
        payment_loan.done_payment_date = date.today()
        payment_loan.user_done = self.env.user.name
        self.action_approve()

        # self.env['account.payment']._compute_payment_method_id()
