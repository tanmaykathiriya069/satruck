from odoo import models,fields,api
from datetime import datetime
from odoo.exceptions import UserError

class SaTruck(models.Model):
    _name = "sa.truck"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Sa Truck"
    _rec_name = 'driver_id'
    _order = 'driver_id desc'

    name = fields.Char("Trip Code")
    email = fields.Char("Email")
    driver_image = fields.Image("Driver Image")
    sequence = fields.Char("Sequence", index=True, copy=False)
    code = fields.Char("Code")
    Company_name_id = fields.Many2one("res.company", string="Company Name", help="Here is company name")
    vehicle_idd = fields.Many2one("vehicle.vehicle", string="Vehicle Model", track_visibility="always")
    driverinfo_ids = fields.One2many("driver.info","satruck_id", string="Driver Information")
    satruck_id = fields.Many2one("sa.truck", string="SA Truck")
    state = fields.Selection([("draft","Draft"), ("to_approve","To Approve"), ("Approve","Approve")], string = "State", default = "draft")
    create_datetime = fields.Datetime("Create Date Time")
    driver_id = fields.Many2one("res.partner", string="Driver Name", track_visibility="always" )
    manager_idd = fields.Many2one("res.users", string="Manager")
    km = fields.Char("KM")
    from_city_id = fields.Many2one("city.city", string="From City")
    to_city_id = fields.Many2one("city.city", string="To City")
    total = fields.Float(compute="get_total")
    sa_addisnal_amount = fields.Float("", compute="get_sa_addisnal_amount")
    total_with_addisnal_amount = fields.Float(compute="get_total_with_addisnal_amount")   
    # sa_truck_id = fields.Many2one('sa.truck', string="SA Truck") 
    count_invoice = fields.Integer("Count Invoice", compute="get_count_invoice")
    account_move_ids = fields.One2many("account.move","sa_truck_id", string="Account Move")
    additional_amount_tax_ids = fields.Many2many("account.tax", string="Additional Amount")

    def get_count_invoice(self):
        for rec in self:
            rec.count_invoice = rec.account_move_ids and len(rec.account_move_ids) or  0

    def delete_all_one2many_line(self):
        for rec in self:
            if rec.driverinfo_ids:
                rec.driverinfo_ids = [(5, 0, 0)]
                return {
                        'effect':{
                            'fadeout':'slow',
                            'type':'rainbow_man',
                            'message':'Driver Expenses Records has been deleted successfully'
                            }
                    }

    @api.onchange('driver_id')
    def res_driver_image(self):
        self.driver_image = self.driver_id.image_1920

    def action_open_invoice(self):
        print(self)
        return {
            'name': "Invoice",
            'type': "ir.actions.act_window",
            'res_model': "account.move",
            "view_mode": "tree",
            "domain": [('sa_truck_id', 'in', self.name)],
        }

    def create_invoice(self):
        new_list = []
        for rec in self.driverinfo_ids:
            vals = {  
                'name' : rec.checklist_id.name,
                'quantity' : rec.quantity,
                'price_unit' : rec.unit_price,
                'tax_ids' : rec.additional_amount_ids,
                'price_subtotal' : rec.total_amount,
            }
            new_list.append((0,None,vals))
        invoice_vals = {
            'move_type' : 'out_invoice',
            'name' : self.name,
            'partner_id' : self.driver_id.id,
            'invoice_date' : self.create_datetime,
            'sa_truck_id': self.id,
            'company_name' : self.Company_name_id.name,
            'invoice_line_ids' : new_list,
        }
        self.env['account.move'].create(invoice_vals)
        print(invoice_vals)

    @api.constrains('driverinfo_ids')
    def checklist_name(self):
        new_list = []
        for rec in self.driverinfo_ids:
            if rec.checklist_id in new_list:
                raise UserError(f"You are Enter {rec.checklist_id.name} More then one Time")
            elif rec.checklist_id.id is False:
                raise UserError("You are not Enter CheckList")
            else:
                new_list.append(rec.checklist_id) 

    @api.constrains('to_city_id')
    def city(self):
        for rec in self:
            if rec.from_city_id == rec.to_city_id:
                raise UserError(f"Please Change City {rec.to_city_id.name} is use in From City")
           
    @api.depends('driverinfo_ids')
    def get_total(self):
        for rec in self:
            rec.total = rec.driverinfo_ids and sum(rec.driverinfo_ids.mapped('subtotal')) or 0

    @api.depends('driverinfo_ids')
    def get_sa_addisnal_amount(self):
        for res in self:
            sa_addisnal_amount = 0
            for rec in self.driverinfo_ids:
                for i in rec.additional_amount_ids:
                    sa_addisnal_amount += (i.amount * rec.subtotal)/100
            res.sa_addisnal_amount = sa_addisnal_amount

    @api.depends('driverinfo_ids')
    def get_total_with_addisnal_amount(self):
        for rec in self:
            rec.total_with_addisnal_amount = rec.driverinfo_ids and sum(rec.driverinfo_ids.mapped('total_amount')) or 0

    @api.model_create_multi
    def create(self, vals):
         for rec in vals: 
            form_code = super(SaTruck, self).create(vals)
            form_code.sequence = self.env['ir.sequence'].next_by_code('sa.truck')
            driver_code = ''
            vehicle_code = ''
            if form_code.driver_id.name != False:
                driver_code = form_code.driver_id.name.upper()[0:3]
            if form_code.vehicle_idd.vehicle_model_id.license_plate != False:
                vehicle_code = form_code.vehicle_idd.vehicle_model_id.license_plate[2:5]
                # print("********* vehicle_code", vehicle_code)
            if driver_code == False:
                # print("********* driver_code", driver_code)
                # print("********* driver_code", vehicle_code)
                print(form_code)
            if vehicle_code == False:
                print(form_code)
            form_code.name = driver_code+'/'+vehicle_code+'/'+form_code.sequence
            return form_code    

    def reset_to_draft(self):
        for rec in self:    
            rec.state = "draft"
            
        quary = """select name from sa_truck"""
        self.env.cr.execute(quary)
        info = self.env.cr.dictfetchall()
        print("queryyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", info)

        return True

    def action_to_approve(self):
        for rec in self:
            rec.state = "to_approve"
        return True

    def action_approve(self):
        temp_id=self.env.ref('sa_truck.sa_truck_email_template')
        # template=self.env['mail.template'].browse(temp_id)
        temp_id.send_mail(self.id)
        for rec in self:
            rec.state = "Approve"

class accountmove(models.Model):
    _inherit = "account.move"

    sa_truck_id = fields.Many2one("sa.truck", string = "Trip Code")
    # trip_code = fields.Char("Trip Code")
    company_name = fields.Char("Company Name") 




    

    