from odoo import fields, models
import io
import base64
import xlsxwriter


class CashFlowReport(models.TransientModel):
    _name = "cash.flow.report"
    _description = "Cash Flow Report"

    name = fields.Char(
        default="Cash Flow Report",
        readonly=True,
    )

    def action_export_excel(self):
        self.ensure_one()

        output = io.BytesIO()

        workbook = xlsxwriter.Workbook(
            output,
            {"in_memory": True},
        )

        worksheet = workbook.add_worksheet(
            "Cash Flow"
        )

        # ==========================
        # Formats
        # ==========================

        title_format = workbook.add_format({
            "bold": True,
            "font_size": 18,
            "font_color": "white",
            "bg_color": "#1F4E78",
            "align": "center",
        })

        report_title = workbook.add_format({
            "bold": True,
            "font_size": 13,
            "bg_color": "#D9EAD3",
            "border": 1,
            "align": "center",
        })

        header = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#4472C4",
            "border": 1,
            "align": "center",
        })

        text = workbook.add_format({
            "border": 1,
        })

        money = workbook.add_format({
            "border": 1,
            "num_format": "#,##0.00",
        })

        total_text = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#305496",
            "border": 1,
        })

        total_money = workbook.add_format({
            "bold": True,
            "font_color": "white",
            "bg_color": "#305496",
            "border": 1,
            "num_format": "#,##0.00",
        })

        company = self.env.company

        worksheet.merge_range(
            "A1:E1",
            company.name,
            title_format,
        )

        worksheet.merge_range(
            "A2:E2",
            "Cash Flow Report",
            report_title,
        )

        worksheet.write("A4", "Report Date")
        worksheet.write("B4", str(fields.Date.today()))

        headers = [
            "Project",
            "Contract",
            "Cash In",
            "Cash Out",
            "Net Cash Flow",
        ]

        for col, value in enumerate(headers):
            worksheet.write(
                5,
                col,
                value,
                header,
            )

        worksheet.set_column("A:B", 25)
        worksheet.set_column("C:E", 20)

        projects = self.env[
            "project.project"
        ].search([])

        row = 6

        total_in = 0
        total_out = 0
        total_net = 0

        for project in projects:

            cash_in = sum(
                self.env["account.move"].search([
                    ("project_id", "=", project.id),
                    ("move_type", "=", "out_invoice"),
                    ("state", "=", "posted"),
                ]).mapped("amount_total")
            )

            cash_out = sum(
                self.env["account.move"].search([
                    ("project_id", "=", project.id),
                    ("move_type", "=", "in_invoice"),
                    ("state", "=", "posted"),
                ]).mapped("amount_total")
            )

            net = cash_in - cash_out

            worksheet.write(
                row,
                0,
                project.name,
                text,
            )

            worksheet.write(
                row,
                1,
                project.contract_id.name if project.contract_id else "",
                text,
            )

            worksheet.write_number(
                row,
                2,
                cash_in,
                money,
            )

            worksheet.write_number(
                row,
                3,
                cash_out,
                money,
            )

            worksheet.write_number(
                row,
                4,
                net,
                money,
            )

            total_in += cash_in
            total_out += cash_out
            total_net += net

            row += 1

        worksheet.write(
            row,
            0,
            "TOTAL",
            total_text,
        )

        worksheet.write_blank(
            row,
            1,
            "",
            total_text,
        )

        worksheet.write_number(
            row,
            2,
            total_in,
            total_money,
        )

        worksheet.write_number(
            row,
            3,
            total_out,
            total_money,
        )

        worksheet.write_number(
            row,
            4,
            total_net,
            total_money,
        )

        worksheet.freeze_panes(6, 0)

        if row > 6:
            worksheet.autofilter(
                5,
                0,
                row - 1,
                4,
            )

        workbook.close()

        output.seek(0)

        attachment = self.env["ir.attachment"].create({
            "name": f"Cash_Flow_Report_{fields.Date.today()}.xlsx",
            "type": "binary",
            "datas": base64.b64encode(output.read()),
            "mimetype": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        })

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }