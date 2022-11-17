# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class HrResgnation(models.Model):
    _name = 'hr.resignation'
    _rec_name = 'name'
    _description = 'Resignation'
    _order = 'name asc, id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name",default='Resignation', required=False, )
    end_incentive = fields.Float(string="End of Service Incentive", required=False, )

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    request_date = fields.Date(string="Request Date", required=False,default=fields.Date.today() )
    department_id = fields.Many2one(comodel_name="hr.department",string="Department")
    job_id = fields.Many2one(comodel_name="hr.job",string="Job Title")
    state = fields.Selection(string="State", selection=[('cancel', 'Cancel'), ('draft', 'Draft'),('approved', 'Approved'), ],default='draft', required=False, )
    resign_date = fields.Date(string="Resignation Date", required=False, )
    approve_date = fields.Date(string="Approve Date", required=False, )
    turnover_reason = fields.Many2one(comodel_name="turnover.reason", string="Reason", required=False, )
    reason = fields.Text(string="Reason", required=False, )
    num_custody = fields.Integer(string="", required=False, compute='compute_num_custody')

    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_("You can delete a record which is in draft state"))
        return super(HrResgnation, self).unlink()


    @api.onchange('employee_id')
    def onchange_employee(self):
        self.update({'department_id':self.employee_id.department_id.id,'job_id':self.employee_id.job_id.id})



    def action_approved(self):
        for custody in self.employee_id.employee_custody_ids:
            if not custody.return_date:
                raise ValidationError(_('Please Check The Custody Of This Employee'))
        self = self.sudo()
        self.employee_id.state = 'resigned'

        # cancel all employee's contracts
        for contract in self.employee_id.contract_ids:
            if contract.state != 'cancel':
                contract.date_end = self.resign_date
                contract.state = 'cancel'
        if self.employee_id.contract_id:
            self.employee_id.contract_id.end_incentive = self.end_incentive
        return self.write({'state':'approved','approve_date':fields.Date.today()})

    def action_cancel(self):
        self.write({'state':'cancel'})

    def action_custody(self):
        ids = self.employee_id.employee_custody_ids.ids

        return {
            'name': "Employee Custody",
            'view_mode': 'tree,form',
            'res_model': 'hr.custody',
            'type': 'ir.actions.act_window',
            'domain': [("id", "in", ids)],
            # 'res_id': newid,
            'context': {'default_employee_id': self.employee_id.id},
        }

    def compute_num_custody(self):
        for rec in self:
            rec.num_custody = len(rec.employee_id.employee_custody_ids)









