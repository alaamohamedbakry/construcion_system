from odoo import models, fields

class ProjectTask(models.Model):
    _inherit = "project.task"

    cost_center_id = fields.Many2one(
        "construction.cost.center",
        string="Cost Center",
    )