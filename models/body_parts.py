# -*- coding: utf-8 -*-
from odoo import fields, models


class BodyParts(models.Model):
    _name = 'body.parts'
    _description = 'Partes del cuerpo que pueden ser lesionadas'

    name = fields.Char(string='Parte del Cuerpo', required=True)

    # _sql_constraints = [
    #     ('name_uniq_body_part', 'unique (name)', 'Esta parte del cuerpo ya está registrada.')
    # ]

