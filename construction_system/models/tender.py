from odoo import models, fields, api


class ConstructionTender(models.Model):
    _inherit = "tender.management"

    customer_id = fields.Many2one("res.partner", string="Customer", tracking=True)

    project_id = fields.Many2one("project.project", string="Project", tracking=True)

    contract_id = fields.Many2one(
        "construction.contract", string="Contract", tracking=True
    )

    estimation_id = fields.Many2one("construction.estimation", string="Estimation")

    boq_id = fields.Many2one("construction.boq", string="BOQ")

    consultant_id = fields.Many2one("res.partner", string="Consultant")

    assigned_engineer_id = fields.Many2one(
        "hr.employee", string="Assigned Engineer", tracking=True
    )

    project_duration = fields.Integer(string="Project Duration (Days)")

    estimated_value = fields.Monetary(string="Estimated Project Value", tracking=True)

    bid_file_id = fields.Many2one("construction.bid.file", string="Bid File")
    currency_id = fields.Many2one(
        "res.currency", default=lambda self: self.env.company.currency_id, readonly=True
    )
