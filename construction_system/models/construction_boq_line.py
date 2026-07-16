from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ConstructionBOQLine(models.Model):
    _name = 'construction.boq.line'
    _description = 'BOQ Lines'

    boq_id = fields.Many2one(
        'construction.boq', 
        string='BOQ Reference', 
        ondelete='cascade', 
        required=True, 
        index=True
    )
    name = fields.Char(
        string='Description/Item Name', 
        required=True
    )
    product_id = fields.Many2one(
        'product.product', 
        string='Material/Service Item',
        required=True
    )
    uom_id = fields.Many2one(
        'uom.uom', 
        string='Unit of Measure', 
        required=True
    )
    


    quantity = fields.Float(
        string='Quantity', 
        default=1.0, 
        required=True
    )
    unit_price = fields.Float(
        string='Unit Price', 
        default=0.0, 
        required=True
    )
    total_cost = fields.Float(
        string='Total Cost', 
        compute='_compute_total_cost', 
        store=True
    )



    @api.depends('quantity', 'unit_price')
    def _compute_total_cost(self):
        for line in self:
            line.total_cost = line.quantity * line.unit_price



    @api.constrains('quantity', 'unit_price')
    def _check_quantity_price(self):
        for line in self:
            if line.quantity <= 0:
                raise ValidationError(_('Quantity must be greater than zero.'))
            if line.unit_price < 0:
                raise ValidationError(_('Unit Price cannot be negative.'))
            
            
    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name
            self.uom_id = self.product_id.uom_id
            self.unit_price = self.product_id.standard_price