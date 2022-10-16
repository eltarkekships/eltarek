from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CentioneDeliveryRequest(models.Model):
    _name = "centione.delivery.request"
    _description = 'Delivery Request'
    _inherit = ['mail.thread']


    def cancel_request(self):
        for delivery_line in self.delivery_lines_ids:
            delivery_line.cancel_line()
        return self.write({'state': 'cancel'})


    def unlink(self):
        raise ValidationError("Sorry you Can't delete delivery request")


    def finished_function(self):
        allowed_users = [self.employee_id.user_id.id, self.create_by.user_id.id]
        if self.env.uid not in allowed_users:
            raise ValidationError(
                "Only the employee who created the delivery request or the assigned employee can finish the request")
        for delivery_line in self.delivery_lines_ids:
            if delivery_line.state == 'warehouse_review' or delivery_line.state == 'requested' or delivery_line.state == 'purchase_request':
                raise ValidationError("You have to received all products line before finish the order.")
        return self.write({'state': 'finished'})


    def transfer_all(self):
        for rec in self:
            return {
                'name': _('Transfer All'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'transfer.all.wizard',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_delivery_id': rec.id,
                    'default_request_lines': rec.delivery_lines_ids.ids,
                },
                'target': 'new'
            }


    def purchase_all(self):
        for rec in self:
            return {
                'name': _('Purchase All'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'purchase.all.wizard',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_delivery_id': rec.id,
                    'default_request_lines': rec.delivery_lines_ids.ids,
                },
                'target': 'new'
            }


    def receive_all(self):
        for rec in self:
            return {
                'name': _('Receive All'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'receive.all.wizard',
                'type': 'ir.actions.act_window',
                'context': {
                    'default_delivery_id': rec.id,
                    'default_request_lines': rec.delivery_lines_ids.filtered(lambda r: r.state == 'purchase_request' or r.state == 'requested').ids,
                },
                'target': 'new'
            }


    def cancel_request_action(self):
        for rec in self:
            return{
                'name': _('Cancel Request'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'cancel.request.wizard',
                'type': 'ir.actions.act_window',
                'target': 'new'

            }

    #
    # def manager_name(self):
    #     self.product_category_manager = self.delivery_lines_ids and self.delivery_lines_ids[0] and \
    #                                     self.delivery_lines_ids[0].product_id and \
    #                                     self.delivery_lines_ids[0].product_id.categ_id and self.delivery_lines_ids[
    #                                         0].product_id.categ_id.manager_id.name or " "

    name = fields.Char(readonly=True)
    employee_id = fields.Many2one('hr.employee', required=True, string="Employee",
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self.env.uid)]))
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)
    delivery_lines_ids = fields.One2many('centione.delivery.request.line', 'request_id',
                                         string='Delivery Request Lines')

    current_user_id = fields.Many2one(comodel_name="res.users", string="Current User", required=False,
                                      default=lambda self: self.env.user, compute='_compute_current_user')
    # product_category_manager = fields.Char(compute=manager_name)
    # analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
    #                                       default=lambda self: self.env['hr.employee'].search(
    #                                           [('user_id', '=', self.env.uid)]).department_id.analytic_account_id.id)
    analytic_account_id = fields.Many2one(comodel_name='account.analytic.account')

    create_by = fields.Many2one('res.users', required=True, string="Created by", default=lambda self: self.env.user)
    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse")
    hide = fields.Boolean(default=False, compute='_compute_current_user')
    is_approved = fields.Boolean(default=False, compute='approve1_checked')
    is_approved2 = fields.Boolean(default=False)
    reason = fields.Text()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('control_approval', 'Control Approval'),
        # ('first_approved_by_manager', 'Employee manager Approval'),
        # ('approved_by_manager', 'Products Cat. managers Approval'),
        ('warehouse_review', 'Warehouse review'),
        ('finished', 'Finished'),
        ('cancel', 'Cancel')
    ], default='draft', index=True, readonly=True, track_visibility='onchange', copy=False)


    def transfers_count(self):
        for rec in self:
            rec.transfer_count = self.env['stock.picking'].search_count(
                [('origin', '=', rec.name)])

    transfer_count = fields.Integer(compute="transfers_count", readonly=True, string="Transfers")


    def delivery_transfers_action(self):
        return {
            'name': _('Transfers'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
        }


    def purchase_req_count(self):
        for rec in self:
            rec.delivery_purchase_count = self.env['centione.purchase.request'].search_count(
                [('origin', '=', rec.name)])

    delivery_purchase_count = fields.Integer(compute="purchase_req_count", readonly=True, string="Purchase Requests")


    def delivery_purchases_action(self):
        return {
            'name': _('Purchase Requests'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'centione.purchase.request',
            'type': 'ir.actions.act_window',
            'domain': [('origin', '=', self.name)],
            'context': {
                'default_employee_id': self.employee_id,
            }
        }

    #
    # def approved_category_manger(self):
    #     for delivery_line in self.delivery_lines_ids:
    #         if delivery_line.state != 'cancel':
    #             delivery_line.state = 'approved_by_manager'
    #     return self.write({'state': 'approved_by_manager'})

    # @api.onchange('name')
    def _compute_current_user(self):
        for rec in self:
            rec.current_user_id = self.env.user
            current_user = self.env.user
            if current_user.id != rec.create_uid.id:
                rec.hide = True
            # elif self.state != 'warehouse_review':
            elif self.state not in ['warehouse_review', 'purchase_request']:
                rec.hide = True
            else:
                rec.hide = False


    def approve1_checked(self):
        for rec in self:
            if rec.employee_id.coach_id.user_id.id == rec.env.uid or self.env.user.has_group(
                    'eltarek_delivery_request_generic.group_employee_manager_approval_show'):
                rec.is_approved = True
            else:
                rec.is_approved = False

    def submit_request(self):
        if self.delivery_lines_ids:
            submit_template = self.env.ref('eltarek_delivery_request_generic.mail_delivery_request_submit_notification')
            mails = []
            # manager_mails = self.env.ref('delivery_request_generic.group_delivery_request_employee_manager').users.sudo().mapped(
            #     'partner_id.email')
            # for mail in manager_mails:
            #     if mail:
            #         mails.append(mail)

            if self.employee_id.coach_id.work_email:
                mails.append(self.employee_id.coach_id.work_email)
            elif self.employee_id.coach_id.user_id and self.employee_id.coach_id.user_id.partner_id.email:
                mails.append(self.employee_id.coach_id.user_id.partner_id.email)

            if mails:
                mails_unique = list(set(mails))
                mails_str = ','.join(mails_unique)
                context = dict(self.env.context)
                context.update({'mails_str': mails_str})
                submit_template.with_context(context).send_mail(self.id, force_send=True)
            for delivery_line in self.delivery_lines_ids:
                delivery_line.is_approved2 = True
                delivery_line.state = 'control_approval'
            return self.write({'state': 'control_approval'})
        else:
            raise ValidationError("Sorry,  You Must Enter Delivery Request Lines First")

    #
    # def first_approve(self):
    #     if self.employee_id.coach_id.user_id.id == self.env.uid or self.env.user.has_group('eltarek_delivery_request_generic.group_employee_manager_approval_show'):
    #         mails = []
    #         # stock_manager_mails = self.env.ref('stock.group_stock_manager').users.sudo().mapped('partner_id.email')
    #         # for mail in stock_manager_mails:
    #         #     if mail:
    #         #         mails.append(mail)
    #
    #         # for line in self.delivery_lines_ids:
    #         #     if line.product_id.categ_id.manager_id:
    #         #         for manager in line.product_id.categ_id.manager_id:
    #         #             mails.append(manager.partner_id.email)

    # if mails:
    #     #     mails_unique = list(set(mails))
    #     #     mails_str = ','.join(mails_unique)
    #     #     context = dict(self.env.context)
    #     #     template = self.env.ref('delivery_request_generic.mail_delivery_request_first_approve_notification')
    #     #     context.update({'mails_str': mails_str})
    #     #     template.with_context(context).send_mail(self.id, force_send=True)
    #
    #     if self.delivery_lines_ids:
    #         for delivery_line in self.delivery_lines_ids:
    #             delivery_line.state = 'warehouse_review'
    #         return self.write({'state': 'warehouse_review'})
    #     else:
    #         raise ValidationError("Sorry,  You Must Enter Delivery Request Lines First")
    # elif self.employee_id.coach_id.user_id != self.env.uid:
    #     raise ValidationError("Sorry,  You Can\'t approve the request")


    def purchase_request(self):
        for delivery_line in self.delivery_lines_ids:
            delivery_line.state = 'received'
        return self.write({'state': 'purchase_request'})


    def purchase_order(self):
        return self.write({'state': 'purchase_order'})


    def warehouse_review(self):
        mails = []
        stock_manager_mails = self.env.ref('stock.group_stock_manager').users.sudo().mapped('partner_id.email')
        for mail in stock_manager_mails:
            if mail:
                mails.append(mail)

        if self.create_by.email:
            mails.append(self.create_by.email)
        elif self.create_by.user_id and self.create_by.user_id.partner_id.email:
            mails.append(self.create_by.user_id.partner_id.email)

        if self.employee_id.work_email:
            mails.append(self.employee_id.work_email)
        elif self.employee_id.user_id and self.employee_id.user_id.partner_id.email:
            mails.append(self.employee_id.user_id.partner_id.email)

        if mails:
            mails_unique = list(set(mails))
            mails_str = ','.join(mails_unique)
            context = dict(self.env.context)
            template = self.env.ref('eltarek_delivery_request_generic.mail_delivery_request_approve_notification')
            context.update({'mails_str': mails_str})
            template.with_context(context).send_mail(self.id, force_send=True)

        self.ensure_one()
        # self._add_followers()
        for delivery_line in self.delivery_lines_ids:
            if not delivery_line.is_approved2:
                raise ValidationError('Sorry you have to determine state for lines first.')
        for delivery_line in self.delivery_lines_ids:
            delivery_line.state = 'warehouse_review'
        return self.write({'state': 'warehouse_review'})

    # def _add_followers(self):
    #     user_ids = []
    #     # user_ids = [line.product_id.categ_id.manager_id.ids for line in self.delivery_lines_ids]
    #     for line in self.delivery_lines_ids :
    #         user_ids.extend(line.product_id.categ_id.manager_id.ids)
    #     self.message_subscribe_users(user_ids=user_ids)


    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'confirm':
            return 'centione_delivery_request.mt_request_created'
        return super(CentioneDeliveryRequest, self)._track_subtype(init_values)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].sudo().next_by_code('centione.delivery.request')
        return super(CentioneDeliveryRequest, self).create(vals)

    # @api.constrains('delivery_lines_ids')
    # def check_product_category(self):
    #     product_category = self.delivery_lines_ids and self.delivery_lines_ids[0].product_id and \
    #                        self.delivery_lines_ids[0].product_id.categ_id.id or False
    #     for product in self.delivery_lines_ids:
    #         if product.product_id.categ_id.id != product_category:
    #             raise ValidationError("You have to choose all the products from the same category")

    # @api.constrains('employee_id')
    # def check_employee_department(self):
    #     if self.employee_id.department_id.id != self.create_by.department_id.id:
    #         raise ValidationError("You have to choose employee from the same department")


class CentioneDeliveryRequestLine(models.Model):
    _name = "centione.delivery.request.line"
    _rec_name = 'product_id'

    def _get_domain(self):
        ids = []
        user_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        products = self.env['product.product'].search(
            [('product_department_ids', 'in', user_employee.department_id.id)])

        for product in products:
            ids.append(product.id)
        return [('id', 'in', ids)]

    product_id = fields.Many2one('product.product', "Product", required=True, )

    # domain = lambda self: self._get_domain()


    def get_products_domain(self):
        for rec in self:
            user_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
            rec.products_dep_domain_ids = self.env['product.product'].search(
                [('product_department_ids', 'in', user_employee.department_id.id)]).ids


    def _check_manager(self):
        for record in self:
            if record.env.user.id in record.product_id.categ_id.manager_id.ids or self.env.user.has_group(
                    'eltarek_delivery_request_generic.group_employee_manager_approval_show'):
                record.is_manager = True
            else:
                record.is_manager = False
        return {}

    current_user_id = fields.Many2one(comodel_name="res.users", string="Current User", required=False,
                                      default=lambda self: self.env.uid, compute='_compute_current_user')
    # product_arabic_name = fields.Char(related='product_id.product_arabic_name')
    # picking_type_id = fields.Many2one('stock.picking.type')
    qty = fields.Float(required=True)
    notes = fields.Text()
    uom_id = fields.Many2one('uom.uom')
    request_id = fields.Many2one('centione.delivery.request')
    is_manager = fields.Boolean(compute=_check_manager)
    received_amount = fields.Float('Received Amount')
    requested_amount = fields.Float('Requested Amount', default=0.0)
    broker_warehouse = fields.Many2one('stock.location', "Broker Warehouse", invisible=True)
    picking_ids = fields.One2many(comodel_name="stock.picking", inverse_name="delivery_request_line_id", string="",
                                  required=False, )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('control_approval', 'Control Approval'),
        # ('first_approved_by_manager', 'First Approval by Employee managers'),
        # ('approved_by_manager', 'Second Approval by Category Products managers'),
        ('warehouse_review', 'Warehouse Review'),
        ('received', 'Received'),
        ('purchase_request', 'Purchase Request'),
        ('cancel', 'Cancel'),
        ('requested', 'Requested')
    ], default='draft', readonly=True)
    is_service = fields.Boolean("Is Service", default=False)
    hide = fields.Boolean(default=False, compute='_compute_current_user')
    is_approved2 = fields.Boolean()
    transfer_quantity = fields.Float(string="Requested Amount")


    # def _compute_current_user(self):
    #     for rec in self:
    #         rec.current_user_id = self.env.user

    @api.onchange('product_id')
    def onchange_product_id(self):
        res = {
            'domain': {'uom_id': [('id', 'in', [])]}
        }
        if self.product_id:
            self.uom_id = self.product_id.uom_id.id
            res['domain']['uom_id'] = [('category_id', '=', self.product_id.uom_id.category_id.id)]
        if self.product_id.type == 'service':
            self.is_service = True
        else:
            self.is_service = False
        return res

    #
    # def approve_line(self):
    #     if self.env.uid in self.product_id.categ_id.manager_id.ids or self.env.user.has_group('eltarek_delivery_request_generic.group_employee_manager_approval_show') :
    #         self.write({'is_approved2': True})
    #     else:
    #         raise ValidationError("Sorry, You Can\'t approve ,You are not the manager of product category")


    def cancel_line(self):
        self.write({'state': 'cancel', 'is_approved2': True})


    def receive_line_function(self):
        if self.qty == self.received_amount:
            self.write({'state': 'received'})


    def _compute_current_user(self):
        for rec in self:
            rec.current_user_id = self.env.user
            current_user = self.env['res.users'].browse(rec.env.uid)
            if current_user.id != rec.create_uid.id:
                rec.hide = True
            elif rec.state != 'requested':
                rec.hide = True
            else:
                rec.hide = False

    @api.constrains('requested_amount', 'qty')
    def check_requested_amount(self):
        if self.requested_amount > self.qty:
            raise ValidationError(_('Total Requested Qty is Greater Than Approved Qty'))

    @api.model
    def create(self, vals):
        print('hi')
        return super(CentioneDeliveryRequestLine, self).create(vals)
