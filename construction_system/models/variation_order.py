from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ConstructionVariationOrder(models.Model):
    _name = "construction.variation.order"
    _description = "Construction Variation Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        default=lambda self: _("New"),
        tracking=True,
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        tracking=True,
    )

    contract_id = fields.Many2one(
        "construction.contract",
        string="Contract",
        required=True,
        tracking=True,
    )

    description = fields.Text(
        string="Description",
        required=True,
    )

    amount = fields.Monetary(
        string="Additional  Amount",
        required=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        related="contract_id.currency_id",
        store=True,
        readonly=True,
    )

    invoice_id = fields.Many2one(
        "account.move",
        string="Customer Invoice",
        readonly=True,
        copy=False,
    )

    invoice_generated = fields.Boolean(default=False)

    state = fields.Selection([
        ("draft", "Draft"),
        ("submitted", "Submitted"),
        ("review", "Engineering Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("invoiced", "Invoiced"),
    ], string="Status", default="draft", tracking=True)





    def action_submit(self):
        self.write({"state": "submitted"})


    def action_review(self):
        self.write({"state": "review"})


    def action_approve(self):
     self.write({"state": "approved"})


    def action_reject(self):
     self.write({"state": "rejected"})


    @api.constrains("amount")
    def _check_amount(self):
        for rec in self:
            if rec.amount <= 0:
                raise ValidationError(_("Variation Amount must be greater than zero."))
            


    def action_update_contract(self):
        self.ensure_one()

        if self.state != "approved":
         raise ValidationError(
            _("Only Approved Variation Orders can update the Contract Value.")
        )

        self.contract_id.contract_value += self.amount



    def action_generate_invoice(self):
        self.ensure_one()

        if self.state != "approved":
            raise ValidationError(
            _("Cannot generate Customer Invoice before Approval.")
        )

        if self.invoice_generated:
         raise ValidationError(
            _("Customer Invoice can be generated only once.")
        )

        invoice = self.env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": self.contract_id.customer_id.id,
        "invoice_date": fields.Date.today(),
        "contract_id": self.contract_id.id,
        "project_id": self.project_id.id,
        "invoice_line_ids": [(0, 0, {
            "name": self.description,
            "quantity": 1,
            "price_unit": self.amount,
        })],
     })

        self.invoice_id = invoice.id
        self.invoice_generated = True
        self.state = "invoiced"



    def action_open_contract(self):
     self.ensure_one()

     return {
        "type": "ir.actions.act_window",
        "name": "Contract",
        "res_model": "construction.contract",
        "view_mode": "form",
        "res_id": self.contract_id.id,
        "target": "current",
     }


    def action_open_invoice(self):
        self.ensure_one()

        if not self.invoice_id:
            return False

        return {
        "type": "ir.actions.act_window",
        "name": "Customer Invoice",
        "res_model": "account.move",
        "view_mode": "form",
        "res_id": self.invoice_id.id,
        "target": "current",
        }