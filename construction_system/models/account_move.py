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


    progress_billing_id = fields.Many2one(
        "construction.progress.billing",
        string="Progress Billing",
        readonly=True,
    )

    contract_id = fields.Many2one(
        "construction.contract",
        string="Contract"
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project"
    )



    def action_post(self):

        res = super().action_post()

        for bill in self:

            if (
                bill.move_type == 'in_invoice'
                and bill.cost_center_id
            ):

                bill.cost_center_id.purchase_cost += bill.amount_untaxed

        return res