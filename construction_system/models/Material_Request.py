from odoo import api, fields, models, _
from odoo.exceptions import UserError 

class ConstructionMaterialRequest(models.Model):
    _name = 'construction.material.request'
    _description = 'Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    name = fields.Char(
        string='Reference',
        default=lambda self: _('New'),
        copy=False,
        readonly=True,
        tracking=True,
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        required=True,
        tracking=True,
    )

    task_id = fields.Many2one(
        'project.task',
        string='Task',
        domain="[('project_id', '=', project_id)]",
        tracking=True,
    )

    requested_by = fields.Many2one(
        'res.users',
        string='Requested By',
        default=lambda self: self.env.user,
        readonly=True,
    )

    request_date = fields.Date(
        string='Request Date',
        default=fields.Date.context_today,
    )

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('issued', 'Issued'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], default='draft', tracking=True)

    line_ids = fields.One2many(
        'construction.material.request.line',
        'request_id',
        string='Material Lines'
    )

    purchase_order_ids = fields.One2many(
        'purchase.order',
        'material_request_id',
        string='Purchase Orders'
    )

    stock_picking_ids = fields.One2many(
        'stock.picking',
        'material_request_id',
        string='Stock Pickings'
    )

    purchase_order_count = fields.Integer(
        compute='_compute_purchase_order_count'
    )

    stock_picking_count = fields.Integer(
        compute='_compute_stock_picking_count'
    )

    total_quantity = fields.Float(
        compute='_compute_totals',
        store=True
    )

    total_amount = fields.Float(
        compute='_compute_totals',
        store=True
    )

    @api.depends('purchase_order_ids')
    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.purchase_order_ids)

    @api.depends('stock_picking_ids')
    def _compute_stock_picking_count(self):
        for rec in self:
            rec.stock_picking_count = len(rec.stock_picking_ids)

    @api.depends('line_ids.quantity', 'line_ids.subtotal')
    def _compute_totals(self):
        for rec in self:
            rec.total_quantity = sum(rec.line_ids.mapped('quantity'))
            rec.total_amount = sum(rec.line_ids.mapped('subtotal'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'construction.material.request'
            ) or _('New')
        return super().create(vals)
    


    def action_submit(self):
        self.write({'state': 'submitted'})

    def action_approve(self):

        for request in self:

            if not request.project_id.site_location_id:
                raise UserError(
                    "Please set Site Location in Project"
                )

            stock_lines = []
            purchase_lines = []

            # Check stock
            for line in request.line_ids:

                available = line.product_id.qty_available

                if available >= line.quantity:
                    stock_lines.append({
                        'line': line,
                        'qty': line.quantity
                    })

                else:

                    if available > 0:
                        stock_lines.append({
                            'line': line,
                            'qty': available
                        })

                    purchase_lines.append({
                        'line': line,
                        'qty': line.quantity - available
                    })


           

            if stock_lines:

                picking = self.env['stock.picking'].create({

                    'picking_type_id': self.env.ref(
                        'stock.picking_type_internal'
                    ).id,

                    'location_id': self.env.ref(
                        'stock.stock_location_stock'
                    ).id,

                    'location_dest_id':
                        request.project_id.site_location_id.id,

                    'origin': request.name,

                    'material_request_id': request.id,
                })


                for item in stock_lines:

                    self.env['stock.move'].create({

                        'name': item['line'].product_id.display_name,

                        'product_id':
                            item['line'].product_id.id,

                        'product_uom_qty':
                            item['qty'],

                        'product_uom':
                            item['line'].product_uom_id.id,

                        'location_id':
                            picking.location_id.id,

                        'location_dest_id':
                            picking.location_dest_id.id,

                        'picking_id':
                            picking.id,
                    })


                picking.action_confirm()
                picking.action_assign()


            

            if purchase_lines:

                vendor = purchase_lines[0]['line'].product_id.seller_ids[:1]

                if not vendor:
                    raise UserError(
                        "Please set Vendor for products"
                    )

                po = self.env['purchase.order'].create({

                    'partner_id':
                        vendor.partner_id.id,

                    'material_request_id':
                        request.id,
                })


                for item in purchase_lines:

                    self.env['purchase.order.line'].create({

                        'order_id': po.id,

                        'product_id':
                            item['line'].product_id.id,

                        'product_qty':
                            item['qty'],

                        'product_uom':
                            item['line'].product_uom_id.id,

                        'price_unit':
                            item['line'].unit_price,

                        'name':
                            item['line'].product_id.display_name,
                    })


                po.button_confirm()


            request.state = 'approved'
    
    
    def action_issue(self):
        
        self.write({'state': 'issued'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

   
   
    def action_view_purchase_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Purchase Orders',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
            'domain': [('material_request_id', '=', self.id)],
            'context': {
                'default_material_request_id': self.id,
            },
        }

    def action_view_stock_pickings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stock Pickings',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
            'domain': [('material_request_id', '=', self.id)],
            'context': {
                'default_material_request_id': self.id,
            },
        }