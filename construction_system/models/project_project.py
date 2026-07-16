from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    cost_center_ids = fields.One2many(
        "construction.cost.center",
        "project_id",
        string="Cost Centers",
    )

    cost_center_count = fields.Integer(compute="_compute_cost_center_count")

    def _compute_cost_center_count(self):
        for project in self:
            project.cost_center_count = len(project.cost_center_ids)

    def action_open_cost_centers(self):
        self.ensure_one()

        return {
            "type": "ir.actions.act_window",
            "name": "Cost Centers",
            "res_model": "construction.cost.center",
            "view_mode": "tree,form",
            "domain": [("project_id", "=", self.id)],
            "context": {
                "default_project_id": self.id,
            },
        }
