from odoo import models, fields, api
from odoo.exceptions import ValidationError

class ConstructionProgressBilling(models.Model):
    _name = "construction.progress.billing"
    _description = "Construction Progress Billing"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('name',default='New',readonly=True,copy=False)
    project_id = fields.Many2one('project.project',string='Project',required=True)
    contract_id = fields.Many2one('construction.contract',string='Contract',required=True)
    customer_id=fields.Many2one("res.partner",string="Customer",related='contract_id.customer_id',readonly=True,store=True)
    billing_date = fields.Date('Billing Date')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted','Submitted'),
        ('approved','Approved'),
        ('invoiced','Invoiced'),
    ], string='state',default='draft',tracking=True)


    contract_value = fields.Monetary(string="Contract Value", related="contract_id.contract_value", store=True, readonly=True,currency_field="currency_id")
    progress_percentage= fields.Float('progress_percentage',required=True)    
    currency_id = fields.Many2one("res.currency", default=lambda self: self.env.company.currency_id)
    invoice_id = fields.Many2one("account.move",string="Customer Invoice",readonly=True)
    invoice_generated = fields.Boolean(string="Invoice Generated",default=False,readonly=True)
    invoice_count = fields.Integer(
    compute="_compute_invoice_count"
)



    current_billing_amount = fields.Monetary(compute='_compute_current_billing_amount', string='Current Billing Amount',store=True,currency_field='currency_id')
    previous_billed_amount = fields.Monetary(string="Previous Billed Amount",compute="_compute_previous_billed_amount",store=True,currency_field="currency_id")
    invoice_amount = fields.Monetary(compute='_compute_invoice_amount', string='Invoice Amount',store=True,currency_field="currency_id")
    
    payment_state = fields.Selection(
    related="invoice_id.payment_state",
    string="Payment Status",
    readonly=True,
    store=True)









    def action_submit(self):
        self.write({
        "state": "submitted"
     })


    def action_approve(self):
        self.write({
        "state": "approved"
        })


    def action_view_invoice(self):
        self.ensure_one()

        return {
        "type": "ir.actions.act_window",
        "name": "Customer Invoice",
        "res_model": "account.move",
        "view_mode": "form",
        "res_id": self.invoice_id.id,
        }
    
    def _compute_invoice_count(self):
     for rec in self:
        rec.invoice_count = 1 if rec.invoice_id else 0



    def action_open_invoice(self):
     self.ensure_one()

     return {
        "type": "ir.actions.act_window",
        "name": "Customer Invoice",
        "res_model": "account.move",
        "view_mode": "form",
        "res_id": self.invoice_id.id,
        }



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
         if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code(
                "construction.progress.billing"
            ) or "New"

        return super().create(vals_list)



    @api.depends('contract_value','progress_percentage')
    def _compute_current_billing_amount(self):
        for rec in self:

         rec.current_billing_amount = (rec.contract_value * rec.progress_percentage/100)


    @api.depends("contract_id", "billing_date", "current_billing_amount")
    def _compute_previous_billed_amount(self):
        for rec in self:
            rec.previous_billed_amount = 0.0

            if not rec.contract_id or not rec.billing_date:
                continue

            previous_billings = self.search([
            ("contract_id", "=", rec.contract_id.id),
            ("billing_date", "<", rec.billing_date),
             ])

            rec.previous_billed_amount = sum(
            previous_billings.mapped("current_billing_amount")
            )
   


    @api.depends('current_billing_amount','previous_billed_amount')
    def _compute_invoice_amount(self):
       for rec in self:
          rec.invoice_amount = max(
            rec.current_billing_amount - rec.previous_billed_amount,
            0.0,
        )
          



    @api.constrains("progress_percentage")
    def _check_progress_percentage(self):
     for rec in self:
        if rec.progress_percentage < 0 or rec.progress_percentage > 100:
            raise ValidationError(
                "Progress Percentage must be between 0 and 100."
            )


    def action_generate_invoice(self):
       self.ensure_one()

       if self.invoice_generated:
        raise ValidationError(
            "Customer Invoice has already been generated."
        )

       invoice = self.env["account.move"].create({
        "move_type": "out_invoice",
        "partner_id": self.customer_id.id,
        "invoice_date": fields.Date.today(),

        "contract_id": self.contract_id.id,
        "project_id": self.project_id.id,
        "progress_billing_id": self.id,

        "invoice_line_ids": [
            (0,0,{
                "name": f"Progress Billing - {self.name}",
                "quantity": 1,
                "price_unit": self.invoice_amount,
            })
        ],
      })

       invoice.action_post()

       self.write({
        "invoice_id": invoice.id,
        "invoice_generated": True,
        "state": "invoiced",
        })

       return {
        "type": "ir.actions.act_window",
        "name": "Customer Invoice",
        "res_model": "account.move",
        "view_mode": "form",
        "res_id": invoice.id,
        }
    

    
