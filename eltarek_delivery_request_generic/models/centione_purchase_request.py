# -*- coding: utf-8 -*-
from odoo import fields, models, api


class CentionePurchaseRequest(models.Model):
    _name = "centione.purchase.request"
    _description = 'Purchase Request'
    _inherit = ['mail.thread']

    name = fields.Char(readonly=True)
    purchase_lines_ids = fields.One2many('centione.purchase.request.line', 'request_id')
    delivery_request_id = fields.Many2one(comodel_name="centione.delivery.request", string="Delivery Request", required=False, )
    initial_order_id = fields.Integer()
    state = fields.Selection([
        ('open', 'Open'),
        # ('approved', 'Approved by Manager'),
        # ('general approved', 'Approved by General Manager'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], default='open', index=True, readonly=True, track_visibility='onchange', copy=False)
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    origin = fields.Char(string="Source Document", required=False, )
    employee_id = fields.Many2one('hr.employee', compute='compute_employee')
    manger_id = fields.Many2one('res.users', related='employee_id.parent_id.user_id', store=True, string='Manager')
    general_manager_approval_date = fields.Datetime(string="General Manager Approval Date")
    manager_approval_date = fields.Datetime(string="Manager Approval Date")
    rfq_date = fields.Datetime(string="RFQ Date")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('centione.purchase.request')

        mails = []
        obj = super(CentionePurchaseRequest, self).create(vals)

        procurement_team_mails = self.env.ref('purchase.group_purchase_manager').users.sudo().mapped('partner_id.email')
        for mail in procurement_team_mails:
            if mail:
                mails.append(mail)

        if mails:
            mails_unique = list(set(mails))
            mails_str = ','.join(mails_unique)
            context = dict(self.env.context)
            template = self.env.ref('eltarek_delivery_request_generic.mail_purchase_request_created_notification')
            context.update({'mails_str': mails_str})
            template.with_context(context).send_mail(obj.id, force_send=True)

        return obj


    def approve_manager(self):
        self.write({
            'state': 'approved',
            'manager_approval_date': fields.Datetime.now()
        })
        for line in self.purchase_lines_ids:
            line.write({
                'state': 'approved'
            })


    def action_manager_approve(self):
        self.write({
            'state': 'done',
            'general_manager_approval_date': fields.Datetime.now()
        })
        for line in self.purchase_lines_ids:
            line.write({
                'state': 'manager approved'
            })



    def action_cancel_by_manager(self):
        self.write({'state': 'cancel'})
        for line in self.purchase_lines_ids:
            line.write({
                'state': 'cancel'
            })


    def action_cancel_all(self):
        self.write({'state': 'cancel'})
        for line in self.purchase_lines_ids:
            line.write({
                'state': 'cancel'
            })


    def done_request(self):
        return self.write({'state': 'done'})

    def compute_employee(self):
        for rec in self:
            origin = rec.origin
            delivery_request = self.env['centione.delivery.request'].search([('name', '=', origin)], limit=1)
            rec.employee_id = delivery_request.employee_id.id

    def request_orders_action(self):
        return {
            'name': 'Purchase Orders',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
        }

    smart_button_request = fields.Integer(compute='compute_request')


    def compute_request(self):
        for rec in self:
            self.smart_button_request = len(rec.env['purchase.order'].search([('origin', '=', rec.name)]))


class CentionePurchaseRequestLine(models.Model):
    _name = "centione.purchase.request.line"

    product_id = fields.Many2one('product.product', required=True)
    # product_arabic_name = fields.Char(related='product_id.product_arabic_name')
    qty = fields.Float()
    cost_price = fields.Float(string="Cost Price")
    delivery_request_line_id = fields.Integer()
    initial_mrp_line_id = fields.Integer()
    uom_id = fields.Many2one('uom.uom')
    uom2_id = fields.Many2one('uom.uom' ,compute='onchange_uom',string='UOM')
    request_id = fields.Many2one('centione.purchase.request')
    picking_type_id = fields.Many2one('stock.picking.type',default=lambda self: self.default_picking_type())
    type = fields.Selection([('sister', 'Sister Company'), ('normal', 'Normal Purchase Request')])
    notes = fields.Text()
    purchase_order_ids = fields.Many2many('purchase.order')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved by Manager'),
        ('manager approved', 'Approved by General Manager'),
        ('done', 'Done'),
        ('cancel', 'Cancel'),
    ], default='draft', readonly=True)
    planned_date = fields.Date("Schedule Date")
    employee_id = fields.Many2one('hr.employee', compute='compute_employee')
    manger_id = fields.Many2one('res.users', related='employee_id.parent_id.user_id', store=True, string='Manager')
    purchase_request_state = fields.Selection([
        ('open', 'Open'),
        ('approved', 'Approved by Manager'),
        ('general approved', 'Approved by General Manager'),
        ('done', 'Done')
    ], default='open', index=True, readonly=True, copy=False, related='request_id.state')

    def default_picking_type(self):
        picking_type = int(self.env['ir.config_parameter'].sudo().get_param('picking_type_first_id', default=0)) or False
        return picking_type


    def cancel_line(self):
        self.ensure_one()
        # Check if all lines of the purchase request have been processed
        # all_lines = self.search([('state', '=', 'draft'), ('request_id', '=', self.request_id.id)])
        # if not all_lines:
        #     self.request_id.state = 'done'
        return self.write({'request_id': False,
                           'state': 'cancel'})

    #
    def manager_approve(self):
        return self.write({'state': 'approved'})
    #
    #
    # def general_manager_approve(self):
    #     return self.write({'state': 'manager approved'})

    @api.onchange('product_id')
    def onchange_product(self):
        self.update({'cost_price': self.product_id.standard_price,
                     'uom_id': self.product_id.uom_id})

    @api.onchange('uom_id')
    def onchange_uom(self):
        for rec in self:
            rec.uom2_id = rec.uom_id.id

    #
    def action_general_manager_approve(self):
        return self.write({'state': 'manager approved'})

    def compute_employee(self):
        for r in self.employee_id:
            r.employee_id = r.request_id.employee_id.id


