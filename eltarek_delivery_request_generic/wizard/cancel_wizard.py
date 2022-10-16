from odoo import api, fields, models, _


class CancelRequestWizard(models.TransientModel):
    _name = 'cancel.request.wizard'
    _description = 'Cancel Request Wizard'

    reason = fields.Text(string="Reason", required=True)
    

    def cancel_request(self):
        for rec in self:
            request = self.env['centione.delivery.request'].browse(self.env.context.get('active_id'))
            request.reason = rec.reason
            request.cancel_request()
    
    