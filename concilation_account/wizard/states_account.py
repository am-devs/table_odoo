from odoo import models, fields, api

class StatesAccount(models.TransientModel):
    _name = 'states.account'
    _description = 'Estados de Cuenta de los Diferentes Bancos'
    

    
    bank_id = fields.Many2one(
        string='bank',
        comodel_name='model.name',
        ondelete='restrict',
    )
    
