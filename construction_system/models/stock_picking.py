from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    material_request_id = fields.Many2one(
        'construction.material.request',
        string='Material Request',
        ondelete='set null',
    )