from odoo import models, fields, api
from enum import Enum


class User(models.Model):
    _name = 'my_api_module.user'
    _description = 'User Authentication'
    _rec_name = 'user_name'

    user_name = fields.Char(string='Username', required=True)
    password = fields.Char(string='Password', required=True)
    role = fields.Selection([
        ('user', 'User'),
        ('admin', 'Admin')
    ], string='Role', default='user', required=True)