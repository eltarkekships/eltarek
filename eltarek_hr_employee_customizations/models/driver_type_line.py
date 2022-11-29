from odoo import fields, models, api, _



class DriverTypeLine(models.Model):
    _name = 'driver.type.line'
    _rec_name = 'name'

    driver_type_id = fields.Many2one('driver.line')
    name = fields.Char('Name')
    truck_number = fields.Char('Truck Number')
    analytic_id = fields.Many2one('account.analytic.account','Analytic Account')
    def name_get(self):
        result = []
        for rec in self:
            result.append(
                (rec.id, '%s - %s' % (rec.name, rec.truck_number)))
        return result