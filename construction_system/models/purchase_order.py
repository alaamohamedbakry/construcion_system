from odoo import models, fields

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    material_request_id = fields.Many2one(
        'construction.material.request',
        string='Material Request',
        ondelete='set null',
    )

    cost_center_id = fields.Many2one(
        "construction.cost.center",
        string="Cost Center",
    )

    analytic_account_id = fields.Many2one(
    "account.analytic.account",
    related="cost_center_id.analytic_account_id",
    store=True,
    readonly=True,
)

    def button_confirm(self):
        res = super().button_confirm()

        for order in self:   
         if order.cost_center_id:
            order.cost_center_id.actual_cost += order.amount_total

        return res
    

    def action_create_invoice(self):
        res = super().action_create_invoice()

        for order in self:

            for invoice in order.invoice_ids:

                invoice.cost_center_id = order.cost_center_id.id
                invoice.purchase_order_id = order.id

        return res