from odoo import models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    material_request_id = fields.Many2one(
        'construction.material.request',
        string='Material Request',
        ondelete='set null',
    )