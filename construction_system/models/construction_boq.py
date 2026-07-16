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
    estimation_ids = fields.One2many(
        'construction.estimation', 
        'boq_id', 
        string='Estimations'
    )
    # contract_ids = fields.One2many(
    #     'construction.contract', 
    #     'project_id', 
    #     string='Contracts'
    # )
    
    estimation_count = fields.Integer(
    string='Estimations',
    compute='_compute_estimation_count'
    )


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


    def _compute_estimation_count(self):
        for rec in self:
            rec.estimation_count = len(rec.estimation_ids)
            
            
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



    def action_create_estimation(self):
        self.ensure_one()

        estimation = self.env['construction.estimation'].create({
            'boq_id': self.id,
        })

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'construction.estimation',
            'res_id': estimation.id,
            'view_mode': 'form',
        }
        
        
        
    def action_view_estimations(self):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'name': 'Estimations',
            'res_model': 'construction.estimation',
            'view_mode': 'tree,form',
            'domain': [
                ('boq_id', '=', self.id)
            ],
            'context': {
                'default_boq_id': self.id,
            },
        }