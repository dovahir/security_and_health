from odoo import models, fields, api

class WorkArea(models.Model):
    _name = "work.area"
    _description = "Área / Lugar Exacto"

    name = fields.Char(string="Nombre del area", required=True)
    work_center_id = fields.Many2one(comodel_name='work.center',
                                     string="Centro de Trabajo",
                                     required=True)

    _sql_constraints = [
        ('name_unique', 'unique (work_center_id, name)', 'Esta área de trabajo ya existe en este centro')
    ]