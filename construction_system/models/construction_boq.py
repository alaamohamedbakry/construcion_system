from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class ConstructionBOQ(models.Model):
    _name = 'construction.boq'
    _description = 'BOQ Header'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        string='BOQ Reference', 
        required=True, 
        copy=False, 
        readonly=True, 
        index=True, 
        default=lambda self: _('New')
    )
    project_id = fields.Many2one(
        'project.project', 
        string='Project', 
        # required=True, 
        index=True, 
        tracking=True
    )
    tender_id = fields.Many2one(
        'construction.tender',
        string='Tender',
        tracking=True
    )
    
    revision = fields.Integer(
        string='Revision', 
        default=0, 
        tracking=True
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('review', 'Review'),
        ('approved', 'Approved')
    ], string='Status', default='draft', tracking=True, index=True)


    boq_line_ids = fields.One2many(
        'construction.boq.line', 
        'boq_id', 
        string='BOQ Lines'
    )
   
    # contract_ids = fields.One2many(
    #     'construction.contract', 
    #     'project_id', 
    #     string='Contracts'
    # )
    
    


    total_quantity = fields.Float(
        string='Total Quantity', 
        compute='_compute_boq_totals', 
        store=True, 
        tracking=True
    )
    total_cost = fields.Float(
        string='Total Cost', 
        compute='_compute_boq_totals', 
        store=True, 
        tracking=True
    )




    @api.depends('boq_line_ids.quantity', 'boq_line_ids.unit_price')
    def _compute_boq_totals(self):
        for boq in self:
            boq.total_quantity = sum(line.quantity for line in boq.boq_line_ids)
            boq.total_cost = sum(line.total_cost for line in boq.boq_line_ids)


          
            
    @api.model
    def create(self, vals):

        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'construction.boq'
            )

        return super().create(vals)



    def unlink(self):
        for boq in self:
            if boq.state == 'approved':
                raise ValidationError(_('You cannot delete an approved BOQ.'))
        return super(ConstructionBOQ, self).unlink()




    def action_review(self):
        self.write({'state': 'review'})

    def action_approve(self):
        self.write({'state': 'approved'})


    def action_create_subcontract(self):
        self.ensure_one()

        subcontract_lines = []

        cost_centers = self.boq_line_ids.filtered("is_subcontract").mapped("cost_center_id")
        if len(cost_centers) > 1:
         raise ValidationError(
        _("Selected subcontract lines must belong to the same Cost Center."))

        if not cost_centers:
            raise ValidationError(
        _("Please select a Cost Center for the subcontract lines.") )

        for line in self.boq_line_ids.filtered("is_subcontract"):
         subcontract_lines.append((0, 0, {
            "boq_line_id": line.id,
            "name": line.name,
            "product_id": line.product_id.id,
            "uom_id": line.uom_id.id,
            "quantity": line.quantity,
            "unit_price": line.unit_price,
        }))

        if not subcontract_lines:
            raise ValidationError(_("Please select at least one subcontract line."))

        return {
        "type": "ir.actions.act_window",
        "res_model": "construction.subcontract",
        "view_mode": "form",
        "target": "current",
        "context": {
            "default_boq_id": self.id,
            "default_project_id": self.project_id.id,
            "default_cost_center_id": cost_centers.id,

            "default_line_ids": subcontract_lines,
         },
        }