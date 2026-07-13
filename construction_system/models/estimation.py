from odoo import models, fields, api


class ConstructionEstimation(models.Model):
    _name = 'construction.estimation'
    _description = 'Cost Estimation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    name = fields.Char(
        string='Estimation Reference',
        required=True,
        default='New'
    )

    boq_id = fields.Many2one(
        'construction.boq',
        string='BOQ Reference',
        required=True
    )

    project_id = fields.Many2one(
        'project.project',
        string='Project',
        related='boq_id.project_id',
        store=True
    )

    estimation_line_ids = fields.One2many(
        'construction.estimation.line',
        'estimation_id',
        string='Estimation Lines'
    )

    total_estimation_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_estimation_cost',
        store=True
    )



    @api.model
    def create(self, vals):
        estimation = super().create(vals)

        if estimation.boq_id:
            lines = []

            for boq_line in estimation.boq_id.boq_line_ids:
                lines.append((0, 0, {
                    'boq_line_id': boq_line.id,
                    'quantity': boq_line.quantity,
                }))

            estimation.estimation_line_ids = lines

        return estimation



    @api.onchange('boq_id')
    def _onchange_boq_id(self):
        self.estimation_line_ids = False

        if self.boq_id:
            lines = []

            for boq_line in self.boq_id.boq_line_ids:
                lines.append((0, 0, {
                    'boq_line_id': boq_line.id,
                    'quantity': boq_line.quantity,
                }))

            self.estimation_line_ids = lines




    @api.depends('estimation_line_ids.total_cost')
    def _compute_total_estimation_cost(self):
        for estimation in self:
            total = 0

            for line in estimation.estimation_line_ids:
                total += line.total_cost

            estimation.total_estimation_cost = total



