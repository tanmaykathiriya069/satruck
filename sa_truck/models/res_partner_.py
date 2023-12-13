from odoo import fields,models,api

class ResPartner(models.Model):
    _inherit="res.partner"

    active_driver = fields.Boolean("Active Driver", default=True)
