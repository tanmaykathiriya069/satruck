from odoo import fields,models,api
from odoo.exceptions import UserError

class CheckList(models.Model):
    _name = "check.list"
    _description = "CheckList"

    name = fields.Char("Name")
    unit_price = fields.Float("Unit price")

    @api.constrains('unit_price')
    def get_unit_price(self):
        if self.unit_price < 0:
            raise UserError("Please Enter Positive Value")

class DriverInfo(models.Model):
    _name = "driver.info"
    _description = "Driver Information"

    remark = fields.Char("Remark")
    checklist_id = fields.Many2one("check.list", string="CheckList")
    states_id = fields.Many2one("states.states", string="States")
    frequency_id = fields.Many2one("frequency.frequency", string="Frequency")
    vehicle_id = fields.Many2one("vehicle.vehicle", string="Vehicle")
    City = fields.Many2one("city.city", string="City")
    satruck_id = fields.Many2one("sa.truck", string="Sa truck")
    additional_amount = fields.Float("Additional Amount(%)")
    unit_price = fields.Float("Unit Price")
    quantity = fields.Float("Quantity", default = 1)
    subtotal = fields.Float("Sub Total" , compute="get_subtotal")
    total_amount = fields.Float("Total Amount (With Additional Amount)", compute="get_total_amount")
    additional_amount_ids = fields.Many2many("account.tax", string="Additional Amount")
    sequence = fields.Integer(string="Seq.")
    @api.constrains('unit_price')
    def uni_price1(self):
        for rec in self:
            if rec.unit_price > rec.checklist_id.unit_price:
                raise UserError(f"Please Enter Less Then {rec.checklist_id.unit_price}")
            elif rec.unit_price < 0:
                raise UserError("Please Enter Positive Value")

    @api.depends('subtotal')
    def get_subtotal(self):
        for rec in self:
            rec.subtotal = rec.unit_price * rec.quantity
    
    @api.depends('subtotal')
    def get_total_amount(self):
        for rec in self:
            for i in rec.additional_amount_ids:
                rec.total_amount = ((i.amount * rec.subtotal)/100)
            rec.total_amount = rec.total_amount + rec.subtotal
               
class States(models.Model):
    _name = "states.states"
    _description = "States"

    name = fields.Char("name")

class Frequency(models.Model):
    _name = "frequency.frequency"
    _description = "frequency"

    name = fields.Char("name")

class Vehicle(models.Model):
    _name = "vehicle.vehicle"
    _description = "Vehicle"

    name = fields.Char("name")
    vehicle_model_id = fields.Many2one("fleet.vehicle", string="Vehicle Model")
    license_plate_no_id = fields.Char("fleet.vehicle", related="vehicle_model_id.license_plate")

class City(models.Model):
    _name = "city.city"
    _description = "City"

    name = fields.Char("City")