from odoo import fields,models,api

class PdfReportQuaryWizardQuery(models.TransientModel):
    _name = "pdf.report.quary.wizard.query"

    start_date_date = fields.Date("Start Date New")
    # end_date = fields.Date("End Date")

    def confirm(self):
        print(self)

    # @api.model
    # def _get_report_values(self, docids, data=None):
    #
    #     query = "SELECT name FROM sa_truck WHERE id=1"
    #
    #
    #     self.env.cr.execute(query)
    #     result = self.env.cr.dictfetchall()
    #
    #     return {
    #         'doc_ids': docids,
    #         'doc_model': 'module.sa_truck',
    #         'docs': result,
    #     }