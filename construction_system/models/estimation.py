from odoo import models, fields, api
from odoo.exceptions import ValidationError



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

    quotation_id = fields.Many2one(
    "sale.order",
    string="Quotation",
    readonly=True,
    copy=False,
    )   

    contract_id = fields.Many2one(
    "construction.contract",
    string="Contract",
    readonly=True,
    copy=False)

    total_estimation_cost = fields.Float(
        string='Total Cost',
        compute='_compute_total_estimation_cost',
        store=True
    )

    quotation_confirmed = fields.Boolean(
    compute="_compute_quotation_confirmed",
    store=True)



    



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


    @api.depends("quotation_id.state")
    def _compute_quotation_confirmed(self):
     for rec in self:
        rec.quotation_confirmed = (
            rec.quotation_id.state == "sale"
        )

    def action_generate_quotation(self):
        self.ensure_one()

        if self.quotation_id:
          raise  ValidationError("Quotation has already Exist")
        
        order_lines=[]
        for line in self.estimation_line_ids:
            if not line.boq_line_id.product_id:
                continue
            order_lines.append((0,0,{
                'product_id':line.boq_line_id.product_id.id,
                'name':line.boq_line_id.name,
                'product_uom_qty':line.quantity,
                'price_unit':line.total_unit_cost
            }))


        quotation = self.env["sale.order"].create({
        "partner_id": self.boq_id.tender_id.customer_id.id,
        "estimation_id": self.id,
        "order_line":order_lines
         })

        self.quotation_id = quotation.id

        return {
        "type": "ir.actions.act_window",
        "res_model": "sale.order",
        "res_id": quotation.id,
        "view_mode": "form",
        }
    


    def action_generate_contract(self):
        self.ensure_one()

        if not self.quotation_id:
          raise ValidationError(
            "Please generate a quotation first."
         )

     
        if self.contract_id:
          raise ValidationError(
            "A contract has already been generated."
            )

        return {
        "type": "ir.actions.act_window",
        "res_model": "construction.contract",
        "view_mode": "form",
        "target": "current",
        "context": {
            "default_customer_id": self.quotation_id.partner_id.id,
            "default_project_id": self.project_id.id,
            "default_tender_id": self.boq_id.tender_id.id,
            "default_contract_value": self.total_estimation_cost,
            "default_estimation_id": self.id,
        },
    }





    def action_open_quotation(self):
         self.ensure_one()

         return {
        "type": "ir.actions.act_window",
        "res_model": "sale.order",
        "view_mode": "form",
        "res_id": self.quotation_id.id,
         }
    

    def action_open_contract(self):
        self.ensure_one()

        return {
        "type": "ir.actions.act_window",
        "res_model": "construction.contract",
        "view_mode": "form",
        "res_id": self.contract_id.id,
        }
        
    @api.model
    def create(self, vals):

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'construction.estimation'
            ) or 'New'

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


