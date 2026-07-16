from odoo import models, fields, api
from odoo.exceptions import ValidationError


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
        currency_field="currency_id",
        readonly=True,
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

        return super().create(vals_list)

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