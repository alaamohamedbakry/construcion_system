from odoo import api, fields, models
from odoo.exceptions import ValidationError

class ConstructionSubcontract(models.Model):
    _name = "construction.subcontract"
    _description = "Subcontract"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(
        string="Reference",
        default="New",
        copy=False,
        readonly=True,
    )

    boq_id = fields.Many2one(
        "construction.boq",
        string="BOQ",
        readonly=True,
    )

    project_id = fields.Many2one(
        "project.project",
        required=True,
        readonly=True,
    )

    contractor_id = fields.Many2one(
        "res.partner",
        string="Subcontractor",
        required=True,
        domain="[('supplier_rank', '>', 0)]",
    )

    contract_date = fields.Date(
        default=fields.Date.today
    )

    state = fields.Selection([
    ("draft", "Draft"),
    ("confirmed", "Confirmed"),
    ("in_progress", "In Progress"),
    ("completed", "Completed"),
    ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    line_ids = fields.One2many(
        "construction.subcontract.line",
        "subcontract_id",
        string="Subcontract Lines",
    )

    total_amount = fields.Float(
        compute="_compute_total_amount",
        store=True,
    )


    purchase_order_id = fields.Many2one(
    "purchase.order",
    string="Purchase Order",
    readonly=True,)

    purchase_order_count = fields.Integer(
    compute="_compute_purchase_order_count")

    vendor_bill_ids = fields.One2many(
    "account.move",
    "subcontract_id",
    string="Vendor Bills")

    currency_id = fields.Many2one(
    "res.currency",
    default=lambda self: self.env.company.currency_id,)
    subcontract_cost = fields.Monetary(
    string="Subcontract Cost",
    compute="_compute_subcontract_cost",
    store=True,
    currency_field="currency_id",)

    cost_center_id = fields.Many2one(
    "construction.cost.center",
    string="Cost Center",
)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = self.env["ir.sequence"].next_by_code(
                    "construction.subcontract"
                ) or "New"

        return super().create(vals_list)

    @api.depends("line_ids.amount")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("amount"))


    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"


    def action_start(self):
        for rec in self:
            rec.state = "in_progress"


    def action_complete(self):
     for rec in self:
        rec.state = "completed"


    def action_cancel(self):
        for rec in self:
         rec.state = "cancelled"


    def _compute_purchase_order_count(self):
        for rec in self:
         rec.purchase_order_count = 1 if rec.purchase_order_id else 0


    def action_create_purchase_order(self):
     self.ensure_one()

     if not self.contractor_id:
        raise ValidationError(
            "Please select subcontractor first."
        )

     order_lines = []

     for line in self.line_ids:

        if not line.product_id:
            raise ValidationError(
                f"Please set product for line: {line.name}"
            )

        if not line.uom_id:
            raise ValidationError(
                f"Please set unit of measure for line: {line.name}"
            )

        order_lines.append((0, 0, {
            "product_id": line.product_id.id,
            "name": line.name,
            "product_qty": line.quantity,
            "product_uom": line.product_id.uom_po_id.id,
            "price_unit": line.unit_price,
            "date_planned": fields.Datetime.now(),
        }))

        print("CURRENT SUBCONTRACT:", self.id, self.name)
        print({"partner_id": self.contractor_id.id,"origin": self.name,"subcontract_id": self.id})


        purchase_order = self.env["purchase.order"].create({
        "partner_id": self.contractor_id.id,
        "origin": self.name,
        "subcontract_id": self.id,
        "cost_center_id": self.cost_center_id.id,
        "order_line": order_lines
         })


        self.purchase_order_id = purchase_order.id

        print(
    "CREATED PO:",
    purchase_order.name,
    purchase_order.subcontract_id.name)

        return {
        "type": "ir.actions.act_window",
        "res_model": "purchase.order",
        "view_mode": "form",
        "res_id": purchase_order.id,
        }
    
    def action_open_purchase_order(self):
        self.ensure_one()

        return {
        "type": "ir.actions.act_window",
        "res_model": "purchase.order",
        "view_mode": "form",
        "res_id": self.purchase_order_id.id,
         }
    
    @api.depends("vendor_bill_ids.amount_untaxed")
    def _compute_subcontract_cost(self):
        for rec in self:
          rec.subcontract_cost = sum(
            rec.vendor_bill_ids.mapped("amount_untaxed")
            )