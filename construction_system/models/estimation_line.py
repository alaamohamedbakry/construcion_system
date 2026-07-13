from odoo import models, fields, api
class ConstructionEstimationLine(models.Model):
    _name = 'construction.estimation.line'
    _description = 'Estimation Line'


    estimation_id = fields.Many2one(
        'construction.estimation',
        string='Estimation',
        ondelete='cascade'
    )

    boq_line_id = fields.Many2one(
        'construction.boq.line',
        string='BOQ Item',
        required=True
    )

    quantity = fields.Float(
        string='Quantity',
        default=1
    )


    material_cost = fields.Float(
        string='Material Cost'
    )

    labor_cost = fields.Float(
        string='Labor Cost'
    )

    equipment_cost = fields.Float(
        string='Equipment Cost'
    )

    subcontractor_cost = fields.Float(
        string='Subcontractor Cost'
    )


    total_unit_cost = fields.Float(
        string='Unit Cost',
        compute='_compute_costs',
        store=True
    )

    total_cost = fields.Float(
        string='Total Cost',
        compute='_compute_costs',
        store=True
    )




    @api.depends(
        'quantity',
        'material_cost',
        'labor_cost',
        'equipment_cost',
        'subcontractor_cost'
    )
    def _compute_costs(self):
        for line in self:

            line.total_unit_cost = (
                line.material_cost +
                line.labor_cost +
                line.equipment_cost +
                line.subcontractor_cost
            )

            line.total_cost = (
                line.quantity *
                line.total_unit_cost
            )