from odoo import fields, models, api, _



class HrDriverType(models.Model):
    _name = 'hr.driver.type'

    name = fields.Char('Name')
