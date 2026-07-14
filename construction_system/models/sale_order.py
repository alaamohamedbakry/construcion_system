from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    estimation_id = fields.Many2one(
        "construction.estimation",
        string="Estimation"
    )


    
