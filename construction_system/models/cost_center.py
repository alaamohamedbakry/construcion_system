from odoo import models, fields, api
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class ConstructionCostCenter(models.Model):
    _name = "construction.cost.center"
    _description = "Construction Cost Center"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "name"

    name = fields.Char(
    string="Cost Center",
    readonly=True,
    copy=False,
    default="New"
    )

    project_id = fields.Many2one(
        "project.project",
        string="Project",
        required=True,
        tracking=True,
    )

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        domain="[('project_id','=',project_id)]",
        tracking=True,
    )

    planned_budget = fields.Monetary(
        string="Planned Budget",
        currency_field="currency_id",
    )

    actual_cost = fields.Monetary(
        string="Actual Cost",
        compute="_compute_actual_cost",
        currency_field="currency_id",
        readonly=True,
        store=True
    )

    remaining_budget = fields.Monetary(
        string="Remaining Budget",
        compute="_compute_budget",
        store=True,
        currency_field="currency_id",
    )

    budget_variance = fields.Monetary(
        string="Budget Variance",
        compute="_compute_budget",
        store=True,
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id,
    )

    state = fields.Selection([
        ("active", "Active"),
        ("monitoring", "Monitoring"),
        ("closed", "Closed"),
    ], default="active", tracking=True)

    analytic_account_id = fields.Many2one(
       "account.analytic.account",
       string='Account Analtyic',
        readonly=True)
    
    material_cost = fields.Monetary(
    string="Material Cost",
    compute="_compute_material_cost",
    currency_field="currency_id",
    readonly=True)

    labor_cost = fields.Monetary(
    string="Labor Cost",
    compute="_compute_labor_cost",
    currency_field="currency_id",
    readonly=True)


    purchase_cost = fields.Monetary(
    string="Purchase Cost",
    currency_field="currency_id",
    readonly=True)

    subcontract_cost = fields.Monetary(
    string="Subcontract Cost",
    currency_field="currency_id",
    readonly=True)

   


    vendor_bill_count = fields.Integer(
    string="Vendor Bills",
    compute="_compute_vendor_bill_count")





    _sql_constraints = [
     (
        "unique_task_cost_center",
        "unique(task_id)",
        "Each task can belong to only one Cost Center."
     )
    ]


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
         if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "construction.cost.center"
            ) or "New"
    

        records = super().create(vals_list)

        plan = self.env["account.analytic.plan"].search(
            [("name", "=", "Construction Cost Centers")],limit=1)


        for rec in records:
            
            analytic = self.env["account.analytic.account"].create({
            "name": rec.name,
            "plan_id": plan.id,

            })

            rec.analytic_account_id = analytic.id

            if rec.task_id:
                rec.task_id.cost_center_id = rec.id

        return records

    @api.depends("planned_budget", "actual_cost")
    def _compute_budget(self):
        for rec in self:
            rec.remaining_budget = rec.planned_budget - rec.actual_cost
            rec.budget_variance = rec.actual_cost - rec.planned_budget

    def action_start_monitoring(self):
        self.write({"state": "monitoring"})


    def action_close(self):
        self.write({"state": "closed"})


    @api.onchange("task_id")
    def _onchange_task_id(self):
      if self.task_id:
        self.project_id = self.task_id.project_id



    def action_open_analytic(self):
        self.ensure_one()

        return {
        "type": "ir.actions.act_window",
        "name": "Analytic Account",
        "res_model": "account.analytic.account",
        "view_mode": "form",
        "res_id": self.analytic_account_id.id,
         }
    

    @api.depends(
    "material_cost",
    "labor_cost",
    "purchase_cost",
    "subcontract_cost",
)
    def _compute_actual_cost(self):
        for rec in self:
            rec.actual_cost = (
            rec.material_cost
            + rec.labor_cost
            + rec.purchase_cost
            + rec.subcontract_cost
         )
            
    def _compute_vendor_bill_count(self):
     for rec in self:
        rec.vendor_bill_count = self.env["account.move"].search_count([
            ("move_type", "=", "in_invoice"),
            ("cost_center_id", "=", rec.id),
        ])



    def action_open_vendor_bills(self):
        self.ensure_one()

        return {
        "type": "ir.actions.act_window",
        "name": "Vendor Bills",
        "res_model": "account.move",
        "view_mode": "list,form",
        "domain": [
            ("move_type", "=", "in_invoice"),
            ("cost_center_id", "=", self.id),
        ],
        "context": {
            "default_cost_center_id": self.id,
        },
        }
    
    @api.depends()
    def _compute_material_cost(self):
     for rec in self:
        moves = self.env["stock.move"].search([
            ("cost_center_id", "=", rec.id),
            ("state", "=", "done"),
        ])

        rec.material_cost = sum(
            move.product_uom_qty * move.product_id.standard_price
            for move in moves
        )