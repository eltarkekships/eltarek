from odoo import api, fields, models


class PurchaseRequestWizard(models.TransientModel):
    _name = 'purchase.request.wizard'

    date_to = fields.Date(string="Date To", required=True, )
    date_from = fields.Date(string="Date From", required=True, )

    # def print_report(self):
    #     recs = self.env[''].search([('','<=',self.),('','>=',)])


