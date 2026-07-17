from odoo import api, fields, models


class ConstructionMaterialRequestLine(models.Model):
    _name = 'construction.material.request.line'
    _description = 'Material Request Line'

    request_id = fields.Many2one(
        'construction.material.request',
        string='Material Request',
        required=True,
        ondelete='cascade'
    )

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True
    )

    description = fields.Char(
        string='Description'
    )

    product_uom_id = fields.Many2one(
        'uom.uom',
        string='Unit of Measure',
        related='product_id.uom_id',
        store=True,
        readonly=True
    )

    quantity = fields.Float(
        string='Requested Quantity',
        default=1.0,
        required=True
    )

    available_qty = fields.Float(
        string='Available Quantity',
        related='product_id.qty_available',
        readonly=True
    )

    unit_price = fields.Float(
        string='Unit Cost',
        related='product_id.standard_price',
        readonly=True
    )

    subtotal = fields.Float(
        string='Subtotal',
        compute='_compute_subtotal',
        store=True
    )



    @api.depends('quantity', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.quantity * rec.unit_price