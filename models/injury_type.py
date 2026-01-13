from odoo import models,fields


class InjuryType(models.Model):
    _name = "injury.type"
    _description = "Tipo de Lesión"

    name = fields.Char(string="Lesión", required=True, tracking=True)
    description = fields.Text(string="Descripción")

    # _sql_constraints = [
    #     ('name_unique_injury', 'unique (name)', 'Este tipo de lesión ya existe')
    # ]

    _name_unique_injury = models.Constraint('unique (name)','Este tipo de lesión ya existe')
