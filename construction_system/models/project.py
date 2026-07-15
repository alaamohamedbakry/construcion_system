from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    site_location_id = fields.Many2one(
        'stock.location',
        string='Site Location',
        domain="[('usage', '=', 'internal')]"
    )