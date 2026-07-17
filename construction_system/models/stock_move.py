from odoo import models, fields


class StockMove(models.Model):
    _inherit = "stock.move"


    cost_center_id = fields.Many2one(
        "construction.cost.center",
        string="Cost Center"
    )


    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account"
    )