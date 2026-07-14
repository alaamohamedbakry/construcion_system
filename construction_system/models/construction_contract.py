from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ConstructionContract(models.Model):
    _name = "construction.contract"
    _description = "Construction Contract"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char( string="Contract Number", readonly=True, copy=False, tracking=True,default='New' )

    customer_id = fields.Many2one("res.partner",string="Customer",required=True,tracking=True,index=True )

    project_id = fields.Many2one("project.project",string="Project", tracking=True,index=True)

    tender_id = fields.Many2one( "construction.tender", string="Tender")

    estimation_id = fields.Many2one("construction.estimation",string="Estimation",readonly=True)

    contract_value = fields.Monetary(string="Contract Value",required=True,currency_field="currency_id",tracking=True)

    currency_id = fields.Many2one("res.currency",default=lambda self: self.env.company.currency_id,)

    start_date = fields.Date(string="Start Date", required=True,tracking=True )

    end_date = fields.Date( string="End Date",required=True, tracking=True,)

    state = fields.Selection([
        ("draft", "Draft"),
        ("approved", "Approved"),
        ("active", "Active"),
        ("completed", "Completed"),
        ("cancel", "Cancelled"),
    ], default="draft", tracking=True)

    notes = fields.Text(string="Notes")


    # invoice_ids = fields.One2many(
    #     "account.move",
    #     "contract_id",
    #     string="Customer Invoices",
    # )

    # variation_order_ids = fields.One2many(
    #     "construction.variation.order",
    #     "contract_id",
    #     string="Variation Orders",
    # )

    # progress_billing_ids = fields.One2many(
    #     "construction.progress.billing",
    #     "contract_id",
    #     string="Progress Billing",
    # )


    # invoice_count = fields.Integer(
    #     compute="_compute_invoice_count"
    # )

    # variation_count = fields.Integer(
    #     compute="_compute_variation_count"
    # )

    # progress_billing_count = fields.Integer(
    #     compute="_compute_progress_billing_count"
    # )


    _sql_constraints = [
        (
            "unique_contract_number",
            "unique(name)",
            "Contract Number must be unique."
        )
    ]





    @api.model_create_multi
    def create(self, vals_list):
     for vals in vals_list:
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "construction.contract"
            ) or "New"

        contracts = super().create(vals_list)

     for contract in contracts:
            if contract.estimation_id:
                contract.estimation_id.contract_id = contract.id

     return contracts
      




    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                if rec.end_date <= rec.start_date:
                    raise ValidationError(
                        "End Date must be after Start Date."
                    )


    def action_approve(self):
        for rec in self:
            rec.state = "approved"

    def action_activate(self):
        for rec in self:
            rec.state = "active"

    def action_complete(self):
        for rec in self:
            rec.state = "completed"

    def action_cancel(self):
        for rec in self:
            rec.state = "cancel"

    # Smart Button Counts

    # @api.depends("invoice_ids")
    # def _compute_invoice_count(self):
    #     for rec in self:
    #         rec.invoice_count = len(rec.invoice_ids)

    # @api.depends("variation_order_ids")
    # def _compute_variation_count(self):
    #     for rec in self:
    #         rec.variation_count = len(rec.variation_order_ids)

    # @api.depends("progress_billing_ids")
    # def _compute_progress_billing_count(self):
    #     for rec in self:
    #         rec.progress_billing_count = len(rec.progress_billing_ids)


    def action_open_project(self):
        self.ensure_one()

        if self.project_id:
            return {
                "type": "ir.actions.act_window",
                "res_model": "project.project",
                "view_mode": "form",
                "res_id": self.project_id.id,
            }

        return {"type": "ir.actions.act_window_close"}

    # def action_open_invoices(self):
    #     self.ensure_one()

    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "account.action_move_out_invoice_type"
    #     )

    #     action["domain"] = [("id", "in", self.invoice_ids.ids)]
    #     action["context"] = {
    #         "default_contract_id": self.id,
    #         "default_move_type": "out_invoice",
    #     }

    #     return action

    # def action_open_progress_billing(self):
    #     self.ensure_one()

    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "construction_system.action_construction_progress_billing"
    #     )

    #     action["domain"] = [
    #         ("contract_id", "=", self.id)
    #     ]

    #     return action

    # def action_open_variation_orders(self):
    #     self.ensure_one()

    #     action = self.env["ir.actions.actions"]._for_xml_id(
    #         "construction_system.action_construction_variation_order"
    #     )

    #     action["domain"] = [
    #         ("contract_id", "=", self.id)
    #     ]

    #     return action