from odoo import models, fields


class AccountMove(models.Model):
    _inherit = "account.move"


    cost_center_id = fields.Many2one(
        "construction.cost.center",
        string="Cost Center"
    )


    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Purchase Order"
    )


    def action_post(self):

        res = super().action_post()

        for bill in self:

            if (
                bill.move_type == 'in_invoice'
                and bill.cost_center_id
            ):

                bill.cost_center_id.actual_cost += bill.amount_total

        return res