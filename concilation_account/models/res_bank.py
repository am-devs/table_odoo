from odoo import api, fields, models, _

from odoo.exceptions import ValidationError
class ResBankInherit(models.Model):
    _inherit = 'res.bank'

    encrypted_key = fields.Char(
        string='Clave Cifrado'
    )
    
    client_id = fields.Char(
        string='Client ID',
    )

    client_secret = fields.Char(
        string='Client Secret',
    )

    